    import pymysql
import os
import time
from pathlib import Path
from curl_cffi.requests import Session
import threading
from queue import Queue

# Configuration
PAGESAVE_PATH = Path("D:/Sharma Danesh/Pagesave/meesho_IN_feasibility/Products_10062025")
PAGESAVE_PATH.mkdir(parents=True, exist_ok=True)
THREAD_COUNT = 12 # Set your desired number of threads here

# Cookies and headers
cookies = {
    'ORDER_BLOCK_EXPERIMENT_COOKIE': '0.56',
    'ANONYMOUS_USER_CONFIG': 'j%3A%7B%22clientId%22%3A%2252f02a3c-3192-4ebf-9c19-b837ec68%22%2C%22instanceId%22%3A%2252f02a3c-3192-4ebf-9c19-b837ec68%22%2C%22xo%22%3A%22eyJ0eXBlIjoiY29tcG9zaXRlIn0%3D.eyJqd3QiOiJleUpvZEhSd2N6b3ZMMjFsWlhOb2J5NWpiMjB2ZG1WeWMybHZiaUk2SWpFaUxDSm9kSFJ3Y3pvdkwyMWxaWE5vYnk1amIyMHZhWE52WDJOdmRXNTBjbmxmWTI5a1pTSTZJa2xPSWl3aVlXeG5Jam9pU0ZNeU5UWWlmUS5leUpwWVhRaU9qRTNORGcxTWpjNU5qVXNJbVY0Y0NJNk1Ua3dOakl3TnprMk5Td2lhSFIwY0hNNkx5OXRaV1Z6YUc4dVkyOXRMMmx1YzNSaGJtTmxYMmxrSWpvaU5USm1NREpoTTJNdE16RTVNaTAwWldKbUxUbGpNVGt0WWpnek4yVmpOamdpTENKb2RIUndjem92TDIxbFpYTm9ieTVqYjIwdllXNXZibmx0YjNWelgzVnpaWEpmYVdRaU9pSmtPV1ZpWmpneE1TMHlPVE5oTFRSaFltUXRPV1ZqWkMwME9HRTVZek13WkdSalpqRWlmUS5xZXN3UHFhN0t5eXlYUmd4QWJabGh2cmlmOE1jaVB6dTRvb1Vud0cyS3V3IiwieG8iOm51bGx9%22%2C%22createdAt%22%3A%222025-05-29T14%3A12%3A45.485Z%22%7D',
    '_gcl_au': '1.1.1461513518.1748527970',
    '_ga': 'GA1.1.952643377.1748527970',
    'bm_ss': 'ab8e18ef4e',
    'bm_mi': '91C339705D77D65FA6E03678A0251897~YAAQZCg0FzHiuC+XAQAAmYanNRvDBlYuldDeXBB+mNNRCd/dLYsbmzxJCKZn5HokYZDcbf8fbjIE3LrKtXjcUepBYL4jiUXi2KCG688OyIhcAXoIW0JtRs69kOZt50CWLQgEfa1qItttXn8/ymuBEIQ9MfKy6L6oDb2VJJUBRpKNIQqtUGiVCpl7HLLrqvjxDAr8dFz4MnZMyxQ165wjpbmXbAzvaa0gYIg3re1DB4YfeQZbBPtuzjggXzcKvJKtza36tsh2iatJozURe+cdpRK/lzQXvac8lgReewNg5E+j2QluE96kyccca3G+~1',
    'ak_bmsc': '5CCF2C71C434E0076B3EC4044B10F5D6~000000000000000000000000000000~YAAQZCg0F9DiuC+XAQAAQYynNRu47dY1kt9pUI0wgFaoppLTI6UFnkvcOQhXSP/gruw0V4HpBzzFGzodR9Qnomfr63BNCxofr1dUPtQwwWlE1QnnYuSKqErLwpHjpJHWpfhojiH3hhD6MysRaJIV5qXtMr0YsUdP425FN32/fbkTEx4uxoqkqGLocJZwSOHBhdl1Wct2/YGL46yuiaoIHK9OQqfKyrhQuOoOOZibOeckqXaNWAc3LdK0r+IPrKTI809gYFqCfwz84ovWWw1kso7YpLdwRXrhUqMk1iR5Ftv2dMlic2a5fnkEezsN+bc4QHWjaCixEfVuxaqbLFL94Fqk2a4n7v+waC/hX4cVE7jzSrtILxN99kR/IpWYtZ1e2sLr7jcuU7hPz9vGLv+vlchK1J67vug8hOCtkD08Jakc8624yY0IgCLDOF8s84lxeemcrMN3iUBMNVgobLtAdH9bhuFTct8CLiLf48w8',
    'INP_POW': '0.8331287342003643',
    '_abck': 'B6484FDEE655069A282C8E862BB2691A~0~YAAQZCg0F4+8uS+XAQAAagqxNQ03OoqyW8zRNAybGbuqoz/xuY7gdtIDIHXywILW1gEAWJ2lfHl1w9GGyspDB9T/PE5fyJvf17CCis6G2da5kzjLQOt1J5npx1F1d2/QP8lv2Um4baglcMHvZNQCFdSO3gyv27WGSjahBOtzkFlP/wcApsgGKM/djabxE3Vs0oS6kEYLGexMvVO/LJkUr4VtWBP71KTsrPL7JCM38t1hVoZWrwWmLmwtf9JkupItG/DX68NJKxOvl6LEUa10VD/v14PFo6TdCp89vZmRv6/d/OT0erDQyK1ohkAK3rwlHXZudjL6vaP54bxgdwlT+Nz3BoAUgFUP87z//29abdfDhAY9Uc4HJca1j1aFtN3sCCR5bqR7JSx96FDC1Xzlv9jPoru+pj7N8TfL4RfKMaALVLqvPn9AojywDcmmzioyatCqecD/43Gg3eoCgx6sQmSdIxLl4cYr3HVQnGnrkLwVqMAYkt+YZBCXcO2fy1bVhZnZJljXSgT5gnGfOlMDf+67mVuk2WDJRgloVi1ZIldLKaN3E6qYBivQFnYY3+G5xjDgMVECS8W7waHI+sEMhIYPOIzFrfbNcCRlmmX/rc4k7UZt0ch12f65kV1RoO1YjpxXi1luMZdTfaJrOGDKOHcsncVJ3TtegNYo2FoJH/BbkwUqBMUav52K~-1~-1~1748955461',
    'bm_so': '372BE54479A8C6BE07FAE72E8BB8D9B0F3E5635412E05825E5B7198F252186B3~YAAQZCg0FyFNuy+XAQAA5bTDNQOLN/XQCSmc54OxZaCwUZ+OioFvhEe/sV/topRcriwdR3ZRA0hfjAo3T8kppwOzuObW8PAvJYpGP+DoxCpnIVCk+rijFHkvgI97bUg1OyR2SoAywvaqYCqvnNtz7DM6IpdtfU1yLkOJ7THF27gaL4q+9IcTQYuDwUuq7NwsmhRq4S3KKg7Rn4wO82+wSH5CZo1TQNze2qwbWz8DABnQ9u/3m6fk0CNAUESd0fiMRl+RXU6I0PcVht1sBGOyE839DQwBO28WNcvKYkjxUCc1CO2nLTJGz/2Vdxi/7zEd4tDZsLnN2SjdRfrQ7NN3rnhkUUz7m66E23EmhKhdZA8JtEdckX73UldQB1qC73VRgX0LogpqjXfULTQUgB8hop5U1qMRwN/8ZuGOpkTObpmB5jdffe6OHA5QMjIYsq42EX6xNOyVBBDTyfOb+3k=',
    'bm_lso': '372BE54479A8C6BE07FAE72E8BB8D9B0F3E5635412E05825E5B7198F252186B3~YAAQZCg0FyFNuy+XAQAA5bTDNQOLN/XQCSmc54OxZaCwUZ+OioFvhEe/sV/topRcriwdR3ZRA0hfjAo3T8kppwOzuObW8PAvJYpGP+DoxCpnIVCk+rijFHkvgI97bUg1OyR2SoAywvaqYCqvnNtz7DM6IpdtfU1yLkOJ7THF27gaL4q+9IcTQYuDwUuq7NwsmhRq4S3KKg7Rn4wO82+wSH5CZo1TQNze2qwbWz8DABnQ9u/3m6fk0CNAUESd0fiMRl+RXU6I0PcVht1sBGOyE839DQwBO28WNcvKYkjxUCc1CO2nLTJGz/2Vdxi/7zEd4tDZsLnN2SjdRfrQ7NN3rnhkUUz7m66E23EmhKhdZA8JtEdckX73UldQB1qC73VRgX0LogpqjXfULTQUgB8hop5U1qMRwN/8ZuGOpkTObpmB5jdffe6OHA5QMjIYsq42EX6xNOyVBBDTyfOb+3k=^1748953708246',
    'bm_sc': '4~1~197042256~YAAQZCg0F2hOuy+XAQAAIMDDNQSJI4nv/16c451ynvVOz1tUtby1CGxWnkgVEGdBfF/okZNIsRE1clQYRPKbyJd3O1RgpT+XbcaivDhQS3IN+SXv2YZhQ/qod5KnsHMGDzJljEoceIyv0iAFfdDGIqIM0mXhFVpb1rFGyZSEYaRwVrHZBS4Vx2iPqq0gGIhHSqldsE7FP7y/NNheIQlHja0OjHSV2mW5itQRkN1BpuXhoQy3fIbXAQcWrV9vQ6hBiHZ3XfPB5mxJ7Rj1nGFMxfNc+KFnJuoq5FYdY2oXYk7qQDG3rTfb2W339nZZn9BIhcI+sShBFvFVXJ3yBa9eWi9/eOzjmwLpOhJUhiQ45alySmL3ATARw2iYop/W7VWVhu2/95IGMwv3HWvnzy5sKcAkxo3m9t0GpbIaAVoFaJUM1yHSozXm4XGC58CFTvaeUphaZNbfxnt70Hr6rZQWsWVGR/yv6/DUf0P6RDCR9Lyz4BtN8qJaM9at5AXAiHBLBJ2uoOWsJUN7YJ+uxnZTQ6R4j9tre3Yvirw1cij0j8rQcdcXT8pBizBKKthWZilCB+TFNCDF5KrfYzyelAgHHw+XXuoRl9J8ObBRQIGBWLO/nZZzXlaMA2QeIL4oCCla5D8U5pOUuqDQuq+J5k3E0frPnPplC5g0VaFY1cChJPdYH1TuoyPdPXDbyiCq+/bFzYg2BHoNq4y6jO5dHrx7bASEMOAAelrnnHr50Ff6g0OQ8qWp5PuzUzpRh8/kiHKqB2CHgN+j',
    'bm_sz': '646C53CDE5362E92EDEA3DAEC3D36EF8~YAAQZCg0F2pOuy+XAQAAIMDDNRu/AdbfKiGc9CekZs+uN71qNNsfEI74ucO+u5V0rO6Y9Lo0iFcTT1ITqGSIrSGswkjP7B0p5VBlvAY36gnd5y4WXpCXFFrTskv1iHxqUqIjN6NRx8rwE514zQJVGm/0kMoaN+LkQvs+H2zI1X9kQdcrROpmvEZ/MAA+p5DCKZ1doRFe2w6xbIeInNpnx2lkD9Z4eGWaEAjFo2pS+NzwHn8oQhu7At2vnDYyFecyQRWaYpk0XTZiTZnTlg0/TSS5vHVrLakEiqxwsxjsVb4v+FwQnd+Qb/usi/n2v6whWsnRfCXwLQAkTDjVhADTcjaI1w9NaoUsHRExtPSJwAxeCJMIphHVuM/hhynrfxlZaq8Yu1zeTjs4JYhn9ZXpjZkMgY1hnAGcjhlYXvV2j+OznoAs1runSmgyaeFAkKligAyBDl3CZKqscsw=~3556144~3227970',
    'bm_s': 'YAAQZCg0F+ROuy+XAQAAKsTDNQM3Rf34DtrO66l7NC51LJusBLh9k+7xd7HhSkEImXV3dkhXP4PD/RF0X8tXdaNghRQSrH2jU0D+7eI5yPHAjCBHwCmFifXnZiawBX05Hp6HEKDqbvi3iniAnX1PmzwYw5Ep3lNPujdwqdzCiPGWqKNP4HWBJBEbZs8Wkofs+ZLR1xHLbijDsr0B+kYOIuD5FvD3b4NdgxkNt5W2Kd0B2Y1h5Qb35ITS03pfo5NOSBkJKhZyVlCuF996yrbWQDjXNdw2DRw3yv7eKAk0hSA4t2ZfKtjig5GYzfUwAa2mCvDVJJ/6NZfcq2wJv39+2BES1Sx8YPuYhzvt/Y9rvYklnD5o2uW+h7U9YIfPVU4pF89svhoskQ82QP486bpoCzN9TIfz+YE6Ox854GD2SU7Lmi81ewJjA02xTXHnkKXsYdGky/4dj/k4fPvtrSDb3G3G1oJTHYUdZNc7NpxzHjZBGD2jvfXJMlOwUVY5ymWlYhZGH9chvZTp2bz1Dd4nNcvv7ss1DNpulVtWzgaS2KPhcZRwXIn/NuEmqT8Y0TiVFXQ0AGBmuxg=',
    'bm_sv': '04CC76DD2CE9E07DF8FFBF5F3807EC6D~YAAQZCg0F+VOuy+XAQAAKsTDNRumu114XTwhYjjpyZ6b3aGG5oire9tIZgkK+5VGG0dIOHnUQpIJHpig1rYY+ezvOmshiA7Xh8gkcj20iBJyjYFr5HH0YOqzPUIM7loDAAyT5B8Ic/wk2c6hd+3E7frDweY9+Ee4z5GmmusQ5qpWOhuwfGmTNTV+D6lrJgKbT2c/PtCexKxaowoWw9FUjyqkiFkOdJOToYINYLRZbN33gLhhL0WXUIyLDNXVGv+Yxg==~1',
    '_ga_NEH2MEG9CT': 'GS2.1.s1748951861$o7$g1$t1748953711$j33$l0$h0',
    'mp_60483c180bee99d71ee5c084d7bb9d20_mixpanel': '%7B%22distinct_id%22%3A%20%221971c6375a5d95-07c058a6b0f9ed-26011f51-e1000-1971c6375a61294%22%2C%22%24device_id%22%3A%20%221971c6375a5d95-07c058a6b0f9ed-26011f51-e1000-1971c6375a61294%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%2C%22%24user_id%22%3A%20%221971c6375a5d95-07c058a6b0f9ed-26011f51-e1000-1971c6375a61294%22%2C%22Is%20Anonymous%22%3A%20%22True%22%2C%22Instance_Id%22%3A%20%2252f02a3c-3192-4ebf-9c19-b837ec68%22%2C%22Session%20ID%22%3A%20%22825d2e28-47cf-4310-b8e0-4d95d1ee%22%2C%22last%20event%20time%22%3A%201748953711678%7D',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    # 'referer': 'https://www.meesho.com/gladly-flip-cover-case-compatible-for-models-realme-narzo-50a-cover-realme-narzo-50a-cover-realme-narzo-50a-flip-cover-realme-narzo-50a-back-cover-realme-narzo-50a-phone-cover-realme-narzo-50a-mobile-cover-realme-narzo-50a-girls-cover/p/1kyf7a',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': "okhttp/4.9.0",
}


# Database connection
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="actowiz",
        database="sy_meesho_vertical_master",
        charset="utf8mb4"
    )

def pagesave_portion(session, link_id):
    page_name = f"{link_id}.html"
    join_path = PAGESAVE_PATH / page_name

    if os.path.exists(join_path):
        print(f"Pagesave already exists: {link_id}")

        return True

    url = f"https://www.meesho.com/messho_lol/p/{link_id}"
    attempts = 3

    for attempt in range(attempts):
        try:
            print(url)
            response = session.get(url, headers=headers, cookies=cookies, timeout=10, impersonate="chrome120")
            if response.status_code == 200 and "__NEXT_DATA__" in response.text:
                with open(join_path, "w", encoding="utf-8") as file:
                    file.write(response.text)

                print(f"Saved: {link_id}")
                return True
            else:
                print(f"Failed to fetch: {link_id}, status code: {response.status_code}")
                time.sleep(2)
                return False
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {link_id}: {e}")
            time.sleep(2)

    print(f"Giving up on: {link_id}")
    return False

def worker(queue):
    db = get_connection()
    session = Session()

    while not queue.empty():
        link_id = queue.get()
        success = pagesave_portion(session, link_id)

        if success:
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        f"UPDATE product_links_20250609 SET Pagesave_status = 'Done' WHERE meesho_pid = '{link_id}'"
                    )
                    db.commit()
            except Exception as e:
                print(f"DB update failed for {link_id}: {e}")
                db.rollback()
        else:
            with db.cursor() as cursor:
                cursor.execute(
                    f"UPDATE product_links_20250609 SET Pagesave_status = 'Error' WHERE meesho_pid = '{link_id}'"
                )
                db.commit()
        queue.task_done()

def main():
    db = get_connection()
    try:
        with db.cursor() as cursor:
            # cursor.execute("SELECT meesho_pid FROM product_links_20250609 WHERE Pagesave_status = 'Pending' LIMIT 101")
            cursor.execute("SELECT meesho_pid FROM product_links_20250610 WHERE Pagesave_status = 'Pending'")
            tasks = [row[0] for row in cursor.fetchall()]
    finally:
        db.close()

    if not tasks:
        print("No pending tasks.")
        return

    queue = Queue()
    for task in tasks:
        queue.put(task)

    print(f"Starting {THREAD_COUNT} workers...")
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, args=(queue,))
        t.start()
        threads.append(t)

    queue.join()

    print("All tasks completed.")

if __name__ == "__main__":
    st = time.time()
    main()
    print(time.time() - st)
