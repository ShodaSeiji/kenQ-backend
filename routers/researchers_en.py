'''
複数のresearcher_idから英語の研究者情報を取得するエンドポイント
'''

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from pykakasi import kakasi

from database.connection import get_db
from database.mymodels import ResearcherInformation

router = APIRouter(prefix="/researchers-en", tags=["英語研究者情報取得"])

# 日本語をローマ字に変換するための設定
kks = kakasi()

def romanize_name(japanese_name: str) -> str:
    """日本語の名前をローマ字に変換（姓名の順序を保持）"""
    if not japanese_name:
        return ""

    # スペースや全角スペースで分割
    parts = japanese_name.replace('　', ' ').split(' ')

    # 各部分をローマ字化して、スペースで結合
    romanized_parts = []
    for part in parts:
        if part:  # 空文字列を除外
            result = kks.convert(part)
            # kakasi の結果から hepburn (ヘボン式ローマ字) を取得
            romanized = ''.join([item['hepburn'] for item in result])
            # 先頭を大文字に
            romanized = romanized.capitalize()
            romanized_parts.append(romanized)

    return ' '.join(romanized_parts)

class ResearcherIdsRequest(BaseModel):
    researcher_ids: List[int]

# 研究者職位の翻訳辞書
POSITION_TRANSLATIONS = {
    "教授": "Professor",
    "准教授": "Associate Professor",
    "助教": "Assistant Professor",
    "講師": "Lecturer",
    "助教授": "Associate Professor",
    "助手": "Research Assistant",
    "研究員": "Researcher",
    "特任助教": "Project Assistant Professor",
    "主任研究員": "Senior Researcher",
    "特任教授": "Project Professor"
}

# 大学名の翻訳辞書
UNIVERSITY_TRANSLATIONS = {
    "北海道大学": "Hokkaido University",
    "東北大学": "Tohoku University",
    "岩手大学": "Iwate University",
    "札幌医科大学": "Sapporo Medical University",
    "宮城大学": "Miyagi University",
    "山形大学": "Yamagata University",
    "会津大学": "University of Aizu",
    "弘前大学": "Hirosaki University",
    "秋田大学": "Akita University",
    "福島大学": "Fukushima University",
    "札幌大学": "Sapporo University",
    "東北学院大学": "Tohoku Gakuin University",
    "岩手医科大学": "Iwate Medical University",
    "宮城学院女子大学": "Miyagi Gakuin Women's University",
    "東北福祉大学": "Tohoku Fukushi University",
    "東京科学大学": "Tokyo Institute of Science",
    "筑波大学": "University of Tsukuba",
    "千葉大学": "Chiba University",
    "十文字学園女子大学": "Jumonji University",
    "群馬大学": "Gunma University",
    "茨城大学": "Ibaraki University",
    "国際基督教大学": "International Christian University",
    "中央大学": "Chuo University",
    "横浜国立大学": "Yokohama National University",
    "東京大学": "The University of Tokyo",
    "上智大学": "Sophia University",
    "電気通信大学": "The University of Electro-Communications",
    "東京外国語大学": "Tokyo University of Foreign Studies",
    "早稲田大学": "Waseda University",
    "慶應義塾大学": "Keio University",
    "東京都立大学": "Tokyo Metropolitan University",
    "東京農工大学": "Tokyo University of Agriculture and Technology",
    "神奈川大学": "Kanagawa University",
    "お茶の水女子大学": "Ochanomizu University",
    "津田塾大学": "Tsuda University",
    "東京学芸大学": "Tokyo Gakugei University",
    "日本大学": "Nihon University",
    "東京理科大学": "Tokyo University of Science",
    "一橋大学": "Hitotsubashi University",
    "埼玉大学": "Saitama University",
    "関東学院大学": "Kanto Gakuin University",
    "東洋大学": "Toyo University",
    "宇都宮大学": "Utsunomiya University",
    "明治大学": "Meiji University",
    "青山学院大学": "Aoyama Gakuin University",
    "立教大学": "Rikkyo University",
    "法政大学": "Hosei University",
    "駒澤大学": "Komazawa University",
    "専修大学": "Senshu University",
    "東海大学": "Tokai University",
    "順天堂大学": "Juntendo University",
    "女子美術大学": "Joshibi University of Art and Design",
    "新潟大学": "Niigata University",
    "山梨大学": "University of Yamanashi",
    "信州大学": "Shinshu University",
    "長岡技術科学大学": "Nagaoka University of Technology",
    "新潟県立大学": "University of Niigata Prefecture",
    "山梨学院大学": "Yamanashi Gakuin University",
    "名古屋大学": "Nagoya University",
    "金沢大学": "Kanazawa University",
    "静岡大学": "Shizuoka University",
    "岐阜大学": "Gifu University",
    "三重大学": "Mie University",
    "名古屋市立大学": "Nagoya City University",
    "静岡県立大学": "University of Shizuoka",
    "富山大学": "University of Toyama",
    "名古屋工業大学": "Nagoya Institute of Technology",
    "中部大学": "Chubu University",
    "南山大学": "Nanzan University",
    "愛知県立大学": "Aichi Prefectural University",
    "名城大学": "Meijo University",
    "愛知大学": "Aichi University",
    "大阪大学": "Osaka University",
    "京都大学": "Kyoto University",
    "神戸大学": "Kobe University",
    "大阪公立大学": "Osaka Metropolitan University",
    "関西大学": "Kansai University",
    "同志社大学": "Doshisha University",
    "立命館大学": "Ritsumeikan University",
    "関西学院大学": "Kwansei Gakuin University",
    "近畿大学": "Kindai University",
    "京都産業大学": "Kyoto Sangyo University",
    "甲南大学": "Konan University",
    "龍谷大学": "Ryukoku University",
    "関西外国語大学": "Kansai Gaidai University",
    "京都女子大学": "Kyoto Women's University",
    "滋賀大学": "Shiga University",
    "奈良女子大学": "Nara Women's University",
    "和歌山大学": "Wakayama University",
    "広島大学": "Hiroshima University",
    "岡山大学": "Okayama University",
    "山口大学": "Yamaguchi University",
    "鳥取大学": "Tottori University",
    "島根大学": "Shimane University",
    "香川大学": "Kagawa University",
    "愛媛大学": "Ehime University",
    "高知大学": "Kochi University",
    "徳島大学": "Tokushima University",
    "広島市立大学": "Hiroshima City University",
    "岡山理科大学": "Okayama University of Science",
    "四国大学": "Shikoku University",
    "九州大学": "Kyushu University",
    "熊本大学": "Kumamoto University",
    "長崎大学": "Nagasaki University",
    "鹿児島大学": "Kagoshima University",
    "宮崎大学": "University of Miyazaki",
    "大分大学": "Oita University",
    "佐賀大学": "Saga University",
    "琉球大学": "University of the Ryukyus",
    "久留米大学": "Kurume University",
    "福岡大学": "Fukuoka University",
    "西南学院大学": "Seinan Gakuin University",
    "九州工業大学": "Kyushu Institute of Technology",
    "福岡教育大学": "Fukuoka University of Education",
    "北九州市立大学": "The University of Kitakyushu",
    "福岡県立大学": "Fukuoka Prefectural University",
    "立命館アジア太平洋大学": "Ritsumeikan Asia Pacific University",
    "鹿屋体育大学": "National Institute of Fitness and Sports in Kanoya"
}

def translate_affiliation(affiliation: str) -> str:
    """大学名を英語に翻訳"""
    if not affiliation:
        return affiliation

    # 翻訳辞書に完全一致するものがあれば使用
    if affiliation in UNIVERSITY_TRANSLATIONS:
        return UNIVERSITY_TRANSLATIONS[affiliation]

    # 部分一致で探す（例: "東京大学大学院" -> "The University of Tokyo Graduate School"）
    for ja_name, en_name in UNIVERSITY_TRANSLATIONS.items():
        if ja_name in affiliation:
            # 大学院などの追加情報を処理
            suffix = affiliation.replace(ja_name, "").strip()
            if "大学院" in suffix:
                return f"{en_name} Graduate School"
            elif suffix:
                return f"{en_name} {suffix}"
            return en_name

    return affiliation

def translate_position(position: str) -> str:
    """職位を英語に翻訳"""
    if not position:
        return position
    return POSITION_TRANSLATIONS.get(position, position)

def translate_department(department: str) -> str:
    """学部・学科名を英語に翻訳（簡易版）"""
    if not department:
        return department

    # 基本的な翻訳パターン（順序重要：長い単語から先に置換）
    translations = {
        # 完全な学部・研究科名を最優先で処理
        "情報理学系研究科": "Graduate School of Information Science and Engineering",
        "医歯学総合研究科": "Graduate School of Medical and Dental Sciences",
        "生命環境科学研究科": "Graduate School of Life and Environmental Sciences",
        "農学生命科学研究科": "Graduate School of Agricultural and Life Sciences",
        "応用生物学群": "School of Applied Biosciences",
        "データサイエンス学類": "College of Data Science",
        "データサイエンス学部": "Faculty of Data Science",
        "応用生物学部": "Faculty of Applied Biosciences",
        "応用生物科学部": "Faculty of Applied Biosciences",
        "生命環境学部": "Faculty of Life and Environmental Sciences",
        "生命科学部": "Faculty of Life Sciences",
        "総合科学部": "Faculty of Interdisciplinary Sciences",
        "園芸学研究科": "Graduate School of Horticulture",
        "園芸学部": "Faculty of Horticulture",
        "経営学部": "Faculty of Business Administration",
        "経営学研究科": "Graduate School of Business Administration",
        "情報基盤センター": "Information Technology Center",
        "基幹研究院": "Institute of Innovative Research",

        # 系研究科パターン
        "医学系研究科": "Graduate School of Medicine",
        "工学系研究科": "Graduate School of Engineering",
        "理学系研究科": "Graduate School of Science",
        "農学系研究科": "Graduate School of Agriculture",
        "園芸学系研究科": "Graduate School of Horticulture",
        "情報理学系": "School of Computing",

        # 学部名
        "教育学研究科": "Graduate School of Education",
        "教育学部": "Faculty of Education",
        "医学部": "Faculty of Medicine",
        "工学部": "Faculty of Engineering",
        "理学部": "Faculty of Science",
        "農学部": "Faculty of Agriculture",
        "法学部": "Faculty of Law",
        "経済学部": "Faculty of Economics",
        "文学部": "Faculty of Literature",
        "薬学部": "Faculty of Pharmacy",
        "歯学部": "Faculty of Dentistry",
        "情報学部": "Faculty of Informatics",
        "環境学部": "Faculty of Environmental Studies",
        "人文学部": "Faculty of Humanities",
        "社会学部": "Faculty of Social Sciences",

        # 複合語・特殊な組織名
        "生命環境科学": "Life and Environmental Sciences",
        "生命科学": "Life Sciences",
        "生命環境": "Life and Environmental Sciences",
        "農学生命科学": "Agricultural and Life Sciences",
        "先端科学技術": "Advanced Science and Technology",
        "オプティクス教育研究センター": "Optics Education and Research Center",
        "オープンイノベーション戦略機構": "Open Innovation Initiative",
        "大学院総合研究部": "Graduate School of Interdisciplinary Research",
        "先端融合学域": "Transdisciplinary Science and Engineering",
        "応用生物科学": "Applied Biosciences",
        "応用生物": "Applied Biology",
        "データサイエンス": "Data Science",
        "情報基盤": "Information Technology",

        # 学部・研究科の一般的な接尾辞
        "研究院": " Research Institute",
        "研究科": " Graduate School",
        "学部": " Faculty",
        "学群": " School",
        "学類": " College",
        "学域": " School",
        "大学院": "Graduate School of ",
        "研究所": " Research Institute",
        "センター": " Center",
        "機構": " Organization",
        "系": " School",

        # 専門分野（学がつくもの）
        "園芸学": "Horticulture",
        "経営学": "Business Administration",
        "工学": "Engineering",
        "理学": "Science",
        "医学": "Medicine",
        "農学": "Agriculture",
        "法学": "Law",
        "経済学": "Economics",
        "文学": "Literature",
        "教育学": "Education",
        "薬学": "Pharmacy",
        "歯学": "Dentistry",
        "情報学": "Informatics",
        "環境学": "Environmental Studies",

        # 単独の用語
        "情報": "Information",
        "環境": "Environmental",
        "人文": "Humanities",
        "社会": "Social Sciences",
        "総合": "Interdisciplinary",
        "先端": "Advanced",
        "生命": "Life Sciences",
        "教育": "Education",
        "園芸": "Horticulture",
        "経営": "Business",
        "医": "Medicine",
        "工": "Engineering",
        "農": "Agriculture",
        "理": "Science",
        "基盤": "Infrastructure",
        "基幹": "Core",
        "応用": "Applied",
        "学野": "Field",

        # その他の用語
        "教授": "Professor",
        "准教授": "Associate Professor",
        "助教": "Assistant Professor"
    }

    result = department
    # 長い単語から順に置換（辞書の順序を保持）
    for ja_term, en_term in translations.items():
        result = result.replace(ja_term, en_term)

    return result.strip()

@router.post("")
def get_researchers_en(
    request: ResearcherIdsRequest,
    db: Session = Depends(get_db)
):
    try:
        # researcher_idsで研究者情報を取得
        stmt = select(ResearcherInformation).where(
            ResearcherInformation.researcher_id.in_(request.researcher_ids)
        )
        researchers = db.execute(stmt).scalars().all()

        # 研究者情報を辞書形式で返す
        researchers_dict = {}
        for researcher in researchers:
            # researcher_name_alphabet が空の場合、日本語名をローマ字化
            english_name = researcher.researcher_name_alphabet
            if not english_name or english_name.strip() == "":
                english_name = romanize_name(researcher.researcher_name)

            researchers_dict[str(researcher.researcher_id)] = {
                "researcher_name": english_name,
                "affiliation": translate_affiliation(researcher.researcher_affiliation_current),
                "department": translate_department(researcher.researcher_department_current) if researcher.researcher_department_current else "",
                "position": translate_position(researcher.researcher_position_current),
                "research_field": researcher.research_field_pi,  # 研究分野はそのまま
                "matching_reason_ja": ""  # マッチング理由は別途取得
            }

        return {
            "researchers": researchers_dict
        }

    except Exception as e:
        print(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")
