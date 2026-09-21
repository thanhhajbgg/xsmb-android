"""Persistent record of actual stakes. No staking recommendations."""
import re
from datetime import datetime

def calculate(points, cost_rate, payout_rate, hits):
    cost = points * cost_rate
    received = None if hits is None else points * payout_rate * hits
    return cost, received, None if received is None else received - cost

def integer(value, label, minimum=1):
    value = str(value).strip()
    if not re.fullmatch(r'[0-9]+', value) or not minimum <= int(value) <= 1000000000:
        raise ValueError(f'{label}: nhập số nguyên từ {minimum} đến 1.000.000.000 (không dấu phân cách).')
    return int(value)

class Ledger:
    def __init__(self, repo):
        self.repo = repo
        with repo.con() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS ledger(
                id INTEGER PRIMARY KEY, day TEXT NOT NULL, number TEXT NOT NULL,
                points INTEGER NOT NULL, cost_rate INTEGER NOT NULL,
                payout_rate INTEGER NOT NULL, manual_hits INTEGER, note TEXT NOT NULL)''')

    def save(self, day, number, points, cost_rate, payout_rate, hits='', note='', row_id=None):
        try:
            day = datetime.strptime(day.strip(), '%d/%m/%Y').date().isoformat()
        except ValueError:
            raise ValueError('Ngày phải hợp lệ, theo dạng DD/MM/YYYY.') from None
        number = number.strip()
        if not re.fullmatch(r'[0-9]{1,2}', number):
            raise ValueError('Số lô phải từ 00 đến 99.')
        vals = (day, number.zfill(2), integer(points,'Điểm'), integer(cost_rate,'Giá mua'),
                integer(payout_rate,'Tiền trả'), None if not str(hits).strip() else integer(hits,'Số lần trúng',0), note.strip())
        with self.repo.con() as c:
            if row_id is None:
                return c.execute('INSERT INTO ledger(day,number,points,cost_rate,payout_rate,manual_hits,note) VALUES(?,?,?,?,?,?,?)', vals).lastrowid
            c.execute('UPDATE ledger SET day=?,number=?,points=?,cost_rate=?,payout_rate=?,manual_hits=?,note=? WHERE id=?', vals+(row_id,))
            return row_id

    def delete(self, row_id):
        with self.repo.con() as c:
            c.execute('DELETE FROM ledger WHERE id=?',(row_id,))

    def rows(self):
        draws = {d.day:d for d in self.repo.list_draws()}
        with self.repo.con() as c:
            records = c.execute('SELECT * FROM ledger ORDER BY day,id').fetchall()
        rows=[]
        for record in records:
            row=dict(zip(('id','day','number','points','cost_rate','payout_rate','manual_hits','note'),record))
            hits=row['manual_hits']
            source='Nhập tay'
            if hits is None:
                draw=draws.get(row['day'])
                hits=None if draw is None else draw.numbers.count(row['number'])
                source='Chờ kết quả' if hits is None else 'Dữ liệu XSMB'
            row.update(hits=hits,source=source)
            row['cost'],row['received'],row['profit']=calculate(row['points'],row['cost_rate'],row['payout_rate'],hits)
            rows.append(row)
        return rows
