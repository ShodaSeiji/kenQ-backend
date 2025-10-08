from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'COMPANY'

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)

    users = relationship("CompanyUser", back_populates="company", cascade="all, delete")

class CompanyUser(Base):
    __tablename__ = 'COMPANY_USER'

    company_user_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('COMPANY.company_id'), nullable=False)
    company_user_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    company = relationship("Company", back_populates="users")
    projects = relationship("ProjectInformation", back_populates="company_user", cascade="all, delete")

class ProjectInformation(Base):
    __tablename__ = "PROJECT_INFORMATION"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    company_user_id = Column(Integer, ForeignKey('COMPANY_USER.company_user_id'), nullable=False)
    project_title = Column(String(255), nullable=False) # 案件タイトル
    project_content = Column(Text, nullable=False) # 案件内容
    industry_category = Column(String(255), nullable=True) # 業種
    business_description = Column(Text, nullable=True) # 事業内容
    university = Column(Text, nullable=False) # 大学
    preferred_researcher_level = Column(String(255), nullable=False) # 研究者階層
    registration_date = Column(DateTime, nullable=False) # 登録日時
    #display_status = Column(Boolean, nullable=False, default=True) # ステータス(True:表示, False:非表示)

    company_user = relationship("CompanyUser", back_populates="projects")
    matchings = relationship("MatchingInformation", back_populates="project")

class MatchingInformation(Base):
    __tablename__ = 'MATCHING_INFORMATION'

    matching_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('PROJECT_INFORMATION.project_id'), nullable=False)
    researcher_id = Column(Integer, ForeignKey('RESEARCHER__INFORMATION.researcher_id'), nullable=False)
    matching_reason = Column(Text, nullable=False) # マッチング理由
    favorite_status = Column(Boolean, default=False, nullable=False) # お気に入りステータス

    project = relationship("ProjectInformation", back_populates="matchings")
    researcher = relationship("ResearcherInformation", back_populates="matchings")

class ResearcherInformation(Base):
    __tablename__ = 'RESEARCHER__INFORMATION'

    researcher_id = Column(Integer, primary_key=True, autoincrement=True)
    researcher_name = Column(String(255), nullable=False)
    researcher_name_kana = Column(String(255), nullable=True)
    researcher_name_alphabet = Column(String(255), nullable=True)
    researcher_affiliation_current = Column(String(255), nullable=False)
    researcher_department_current = Column(String(255), nullable=True)
    researcher_position_current = Column(String(255), nullable=False)
    researcher_affiliations_past = Column(String(255), nullable=True)
    research_field_pi = Column(String(255), nullable=False)
    keywords_pi = Column(String(255), nullable=False)
    kaken_url = Column(String(255), nullable=False)

    matchings = relationship("MatchingInformation", back_populates="researcher", cascade="all, delete")

