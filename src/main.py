import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, DL_LINK_PATTERN,
    EXPECTED_STATUS, MAIN_DOC_URL,
    MAIN_PEPS_URL, OutputTypeChoices
    )
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(
        soup,
        'section',
        attrs={'id': 'what-s-new-in-python'}
        )
    div_with_ul = find_tag(
        main_div,
        'div',
        attrs={'class': 'toctree-wrapper compound'}
        )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [(
        'Ссылка на статью', 'Заголовок', 'Редактор, автор'
        )]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if not response:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1, dl = find_tag(soup, 'h1'), find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if not response:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(
        soup,
        'div',
        attrs={'class': 'sphinxsidebarwrapper'}
        )
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        raise Exception('Не найден список c версиями Python')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        link = a_tag['href']
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(
        soup,
        'div',
        attrs={'role': 'main'}
        )
    table_tag = find_tag(
        main_tag,
        'table',
        attrs={'class': 'docutils'}
        )
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        attrs={'href': re.compile(DL_LINK_PATTERN)}
        )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)
    if not response:
        return
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, MAIN_PEPS_URL)
    if response is None:
        return None
    soup = BeautifulSoup(response.text, features='lxml')
    peps = soup.find_all(attrs={'class': re.compile('table*.')})
    results = [('Cтатус', 'Количество')]
    statuses_count = {}
    different_statuses_logs = []

    for pep in tqdm(peps):
        tr_tags = pep.tbody.find_all('tr')
        for tr_tag in tqdm(tr_tags):
            preview_status = tr_tag.text[1:2]
            link = tr_tag.select_one('[href]')['href']
            page_pep_url = urljoin(MAIN_PEPS_URL, link)
            response = get_response(session, page_pep_url)
            if response is None:
                continue
            soup = BeautifulSoup(response.text, features='lxml')
            page_status = soup.find(
                string='Status').findNext('dd').text

            status = EXPECTED_STATUS.get(preview_status, '')
            if page_status not in status:
                log = f'''
                Несовпадающие статусы:
                {page_pep_url}
                Статус в карточке: {page_status}
                Ожидаемые статусы: {status}'''
                different_statuses_logs.append(log)

            if preview_status not in EXPECTED_STATUS.keys():
                preview_status = ''
            if statuses_count.get(page_status):
                statuses_count[page_status] += 1
            else:
                statuses_count[page_status] = 1

    for log in different_statuses_logs:
        logging.info(log)

    results.extend(
        [(key, value) for key, value in statuses_count.items()]
        )
    results.append(('Total', sum(statuses_count.values())))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(
        MODE_TO_FUNCTION.keys()
        )
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if parser_mode == 'pep':
        args.output = OutputTypeChoices.FILE
    if results:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
