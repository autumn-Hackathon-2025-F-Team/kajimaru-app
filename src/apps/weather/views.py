import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page

def _to_category(code: int) -> str:
    if code in (0,):
        return 'sunny'
    if code in (1, 2, 3, 45, 48):
        return 'cloudy'
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99):
        return 'rainy'
    if code in (71, 73, 75, 77, 85, 86):
        return 'snow'
    return 'cloudy'

RECO = {
    "sunny": {
        "label": "晴れ",
        "emoji": "☀️",
        "one_liner": "洗濯＆大物を一気に！シーツやカーペット日干しのチャンス。",
        "tasks": ["シーツ・布団干し", "カーペット天日干し", "ベランダ掃除", "窓拭き（外側）"],
    },
    "cloudy": {
        "label": "くもり",
        "emoji": "⛅",
        "one_liner": "外は微妙…室内の“コツコツ系”を進める日。",
        "tasks": ["冷蔵庫の中の棚拭き", "洗面台・水栓の水垢取り", "衣類の整理（仕分け）", "掃除機がけ"],
    },
    "rain": {
        "label": "雨",
        "emoji": "🌧️",
        "one_liner": "外出控えでじっくり。カビ対策＆キッチン周りの徹底を！",
        "tasks": ["浴室のカビ取り", "排水口のぬめり取り", "コンロ＆レンジフードの油汚れ", "生乾き防止に除湿（浴室乾燥/除湿機）"],
    },
    "snow": {
        "label": "雪",
        "emoji": "❄️",
        "one_liner": "安全第一。暖かく、家の中を整えるメンテ系がおすすめ。",
        "tasks": ["加湿器の洗浄", "窓の結露拭き＆カビ予防", "ストック品の棚卸し", "玄関の泥汚れ対策"],
    },
}

@require_GET
@cache_page(60 * 30)
def weather_recommendations(request):
    lat, lon = 35.6812, 139.7671
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=weather_code,temperature_2m"
        "&timezone=Asia%2FTokyo"
    )
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        data = r.json()
        cur = data.get('current', {})
        code = int(cur.get('weather_code', 3))
        temp = cur.get('temprature_2m')
    except Exception:
        code, temp = 3, None
    
    cat = _to_category(code)
    rec = RECO[cat]
    return JsonResponse({
        'ok': True,
        'category': cat,
        'label': rec['label'],
        'emoji': rec['emoji'],
        'temperature': temp,
        'one_liner': rec['one_liner'],
        'tasks': rec['tasks'],
    })