
from src.models import Draw
from src.storage import Repository
from src.app_service import AppService

def test_analyze_returns_explicit_next_draw_date(tmp_path):
    repo=Repository(tmp_path/"x.db")
    repo.save_draw(Draw("2026-09-15", tuple(f"{i:02d}" for i in range(27)), "12345", "test"))
    result=AppService(repo).analyze()
    assert result.target_day == "2026-09-16"
    assert len(result.ranking) == 100
