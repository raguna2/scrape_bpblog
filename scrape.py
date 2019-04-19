import csv

from bs4 import BeautifulSoup
import requests

BASE_URL = 'http://blog.pyq.jp/archive'
ARCHIVE_DICTS = {
    # TODO: 現在の日付から2017年度以降を生成
    '2019': (1, 4),
    '2018': (1, 12),
    '2017': (7, 12)
}


class Entry:
    def __init__(self, title, link, posted_date, categories):
        self.title = title
        self.link = link
        self.posted_date = posted_date
        self.categories = categories

    def export_csv(self):
        for main_category in self.categories:
            csv_row_list = [self.title, self.link, self.posted_date]
            csv_row_list.append(main_category)

            # 紐付いてるカテゴリからメインカテゴリとなるものを除いた差分
            diff = list(set(self.categories) - set([main_category]))
            csv_row_list = csv_row_list + diff

            with open('blog_entry_bp.csv', 'a') as f:
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow(csv_row_list)


def get_url_lists():
    """対象urlのリストを生成する関数
    Returns
    ----------
    url_lists: list(str, str)
        URLのリスト

    Notes
    ------------
    返り値のリストに含まれるURLは

    http://blog.pyq.jp/archive/<year>/<month>形式
    """
    url_lists = []
    for key, values in ARCHIVE_DICTS.items():
        start, end = values
        list_ = [f"{BASE_URL}/{key}/{month}" for month in range(start, end)]
        url_lists = url_lists + list_

    return url_lists


def fetch_entry_section(url):
    """月ごとのブログ記事一覧ページからsectionタグを全て取得"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 各記事のかたまりはsectionタグで囲われている
    sections = soup.find_all('section', class_='archive-entry')
    return sections


def generate_entry_instance(sec):
    """entryインスタンスを生成する"""
    title = sec.find('a', class_='entry-title-link').text.strip()
    link = sec.find('a', class_='entry-title-link').get('href').strip()
    posted_date = sec.find('time').text.strip()
    categories_atags = sec.find_all('a', class_='archive-category-link')
    categories = [category.text for category in categories_atags]
    entry = Entry(
        title,
        link,
        posted_date,
        categories,
    )
    return entry


def main():
    """
    Notes
    ---------------------
    実行方法: python scrape.pyを実行
    """

    with open('blog_entry_bp.csv', 'a') as f:
        # ファイルを上書き(ファイルがなければ新規作成)し、ヘッダーを追加
        header = [
            'タイトル', 'リンク', '投稿日時',
            'カテゴリ1', 'カテゴリ2', 'カテゴリ3', 'カテゴリ4'
        ]
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(header)

    # urlのリストを生成
    url_lists = get_url_lists()

    for url in url_lists:
        sections = fetch_entry_section(url)  # 1ヶ月分

        for sec in sections:
            entry = generate_entry_instance(sec)
            entry.export_csv()


if __name__ == '__main__':
    main()
