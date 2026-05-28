def generate_prompt(plan_name, plan_date, daily_available_minutes, feedback = ''):

  word =f'''
  あなたは、初心者が目標達成まで進めるための計画作成アシスタントです。\

  目的:\
  ユーザーの目標を、小さく着手しやすいタスクへ分解してください。\
  
  入力:\
  plan_name(プラン名): {plan_name}\
  plan_date（受験日）: {plan_date}\
  daily_available_minutes（1日に学習可能時間（分））: {daily_available_minutes}\
  調整用フィードバック : {feedback}\
  

  必須条件:\
  - タスクは本日からplan_date（受験日）までのプランで生成する\
  - タスクは初心者でも始められる粒度にしてください\
  - genreは、plan_name（受験する試験）の実在する試験範囲・シラバス・学習項目を元に設定してください\
  - 1つのgenreは1つの学習テーマ（大分類）とし、1つのgenreに対して複数の具体的なタスクを作成してください\
  - 1タスクあたりの想定作業時間は5分〜60分程度にしてください\
  - タスクは期限までに出題範囲全体で、完了可能な現実的な順序にしてください\
  - 抽象的な表現を避け、実際に手を動かせる内容にしてください\
  - 出力は必ずJSONのみで返してください\
  - 説明文やコードブロックは不要です\
  - feedbackがある場合は考慮してプランを調整してください\
  - ただしfeedbackの内容だけに偏らず、試験範囲全体の学習バランス・期限・学習可能時間も考慮してください\

  出力形式例:\
  以下は、基本情報技術者試験を例にした際の出力例です

  {{
    "plans": [
      {{
        "index": "1",
        "planname": "短期集中プラン",
        "tasks": [
          {{
            "name": "アルゴリズムとプログラミング",
            "genre": "基礎理論",
            "task_start_date": "2026-05-01",
            "task_end_date": "2026-05-01"
          }}
        ]
      }},
      {{
        "index": "2",
        "planname": "バランス重視プラン",
        "tasks": []
      }},
      {{
        "index": "3",
        "planname": "ゆったり進めるプラン",
        "tasks": []
      }}
    ]
  }}

  '''

  return word


  # 入力:\
  # plan_name(プラン名): "G検定"\
  # plan_start_date（プラン開始日）: 2026/05/01\
  # plan_end_date（受験日）: 2026/07/03\
  # daily_available_minutes（1日に学習可能時間（分））: 60\


  # goal: {{goal}}\
  # deadline: {{deadline}}\
  # daily_available_minutes: {{daily_available_minutes}}\


  # {
  #   "tasks": [
  #     {
  #       "id": "1",
  #       "title": "情報の基礎理論",
  #       "genre": "基礎理論",
  # 			"task_start_date": "2026-04-10",
  # 			"task_end_date": "2026-04-12",
  #     },
  #     {
  #       "id": "2",
  #       "title": "アルゴリズムとプログラミング",
  #       "genre": "基礎理論",
  # 			"task_start_date": "2026-04-13",
  # 			"task_end_date": "2026-04-15",
  #     },
  #     ...
  #   ]
  # }


def regenerate_prompt(original_data, option):
  word =f'''
  あなたは、初心者が目標達成まで進めるための計画作成アシスタントです。\

  目的:\
  ユーザーの目標を、小さく着手しやすいタスクへ分解してください。\
  
  入力:\
  original_data(jsonの修正前データ): {original_data}\
  option（jsonデータ調整用の文言）: {option}\
  

  必須条件:\
  - タスクは初心者でも始められる粒度にしてください\
  - 1タスクあたりの想定作業時間は5分〜60分程度にしてください\
  - タスクは期限までに完了可能な現実的な順序にしてください\
  - 抽象的な表現を避け、実際に手を動かせる内容にしてください\
  - 出力は必ずJSONのみで返してください\
  - 説明文やコードブロックは不要です\
  - original_dataをoptionを考慮して再生成してください\

  出力形式例:\
  以下は、基本情報技術者試験を例にした際の出力例です

  {{
    "plans": [
      {{
        "index": "1",
        "planname": "短期集中プラン",
        "tasks": [
          {{
            "name": "アルゴリズムとプログラミング",
            "genre": "基礎理論",
            "task_start_date": "2026-05-01",
            "task_end_date": "2026-05-01"
          }}
        ]
      }},
      {{
        "index": "2",
        "planname": "バランス重視プラン",
        "tasks": []
      }},
      {{
        "index": "3",
        "planname": "ゆったり進めるプラン",
        "tasks": []
      }}
    ]
  }}

  '''

  return word