"""
FAQプリセットデータ定義
新規施設登録時に自動投入される30個のFAQテンプレート
"""

FAQ_PRESETS = [
    # Basic (8 questions)
    {
        "category": "basic",
        "intent_key": "basic_quiet_hours",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "夜間の静音ルールはありますか？",
                "answer": "22時以降は他のゲストへの配慮をお願いします。通話や会話は共用スペースで行ってください。"
            },
            {
                "language": "en",
                "question": "Is there a quiet rule at night?",
                "answer": "Please keep noise to a minimum after 10:00 PM. Phone calls and conversations should be done in common areas."
            }
        ]
    },
    {
        "category": "basic",
        "intent_key": "basic_smoking_policy",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "館内での喫煙ルールを教えてください。",
                "answer": "建物内は全面禁煙です。指定された屋外喫煙場所のみ利用できます。"
            },
            {
                "language": "en",
                "question": "What is the smoking policy?",
                "answer": "Smoking is prohibited inside the building. Please use the designated outdoor smoking area."
            }
        ]
    },
    {
        "category": "basic",
        "intent_key": "basic_common_areas",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "共用スペースは誰でも使えますか？",
                "answer": "宿泊中のゲストであれば自由に利用できます。長時間の占有はご遠慮ください。"
            },
            {
                "language": "en",
                "question": "Can anyone use the common areas?",
                "answer": "All staying guests may use them freely. Please avoid occupying them for long periods."
            }
        ]
    },
    {
        "category": "basic",
        "intent_key": "basic_enter_other_rooms",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "他のゲストの部屋に入ってもいいですか？",
                "answer": "セキュリティ上、他のゲストの部屋への立ち入りは禁止しています。"
            },
            {
                "language": "en",
                "question": "Can I enter another guest's room?",
                "answer": "For security reasons, entering other guests' rooms is not allowed."
            }
        ]
    },
    {
        "category": "basic",
        "intent_key": "basic_drinking_alcohol",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "館内で飲酒しても問題ありませんか？",
                "answer": "節度を守っていただければ可能です。騒音や迷惑行為は禁止です。"
            },
            {
                "language": "en",
                "question": "Is drinking alcohol allowed inside the property?",
                "answer": "Yes, as long as it is done responsibly. Please avoid noise or disturbing behavior."
            }
        ]
    },
    {
        "category": "basic",
        "intent_key": "basic_contact_during_stay",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "滞在中の問い合わせはどこから行えばいいですか？",
                "answer": "滞在中はこのチャットをご利用ください。チェックアウト後は対応できません。"
            },
            {
                "language": "en",
                "question": "How can I contact you during my stay?",
                "answer": "Please use this chat during your stay. Support is not available after check-out."
            }
        ]
    },
    {
        "category": "basic",
        "intent_key": "basic_before_checkout",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "チェックアウト前にやるべきことは何ですか？",
                "answer": "私物の回収、ゴミの処分、備品の返却をお願いします。"
            },
            {
                "language": "en",
                "question": "What should I do before check-out?",
                "answer": "Please collect your belongings, dispose of trash, and return any provided items."
            }
        ]
    },
    {
        "category": "basic",
        "intent_key": "basic_return_sheets_towels",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "シーツ類とバスタオルはどこに返却しますか？",
                "answer": "シーツ類と枕カバーはロビーの赤い回収ボックスに、バスタオルは青い回収ボックスに入れてからチェックアウトしてください。"
            },
            {
                "language": "en",
                "question": "Where should I return sheets and bath towels?",
                "answer": "Please put sheets and pillowcases into the red collection box in the lobby, and bath towels into the blue collection box before check-out."
            }
        ]
    },
    # Facilities (8 questions)
    {
        "category": "facilities",
        "intent_key": "facilities_shower_anytime",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "シャワーはいつでも使えますか？",
                "answer": "24時間利用可能です。使用後は換気と簡単な清掃をお願いします。"
            },
            {
                "language": "en",
                "question": "Can I use the shower at any time?",
                "answer": "Yes, showers are available 24 hours a day. Please ventilate and clean lightly after use."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_hair_dryer_location",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "ドライヤーはどこにありますか？",
                "answer": "洗面エリアの棚に設置しています。使用後は元の場所へ戻してください。"
            },
            {
                "language": "en",
                "question": "Where can I find a hair dryer?",
                "answer": "Hair dryers are located on the shelves in the wash area. Please return them after use."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_shared_kitchen",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "共用キッチンは自由に使えますか？",
                "answer": "使用可能です。利用後は必ず清掃し、調理器具を元の場所に戻してください。"
            },
            {
                "language": "en",
                "question": "Can I use the shared kitchen?",
                "answer": "Yes. Please clean after use and return all utensils to their original places."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_refrigerator_storage",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "冷蔵庫に物を入れてもいいですか？",
                "answer": "共用冷蔵庫を利用できます。名前と日付を記入してください。"
            },
            {
                "language": "en",
                "question": "Can I store items in the refrigerator?",
                "answer": "Yes, please label your items with your name and date."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_washer_dryer",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "洗濯機と乾燥機の使い方を教えてください。",
                "answer": "指定エリアにあります。料金と操作方法は掲示をご確認ください。"
            },
            {
                "language": "en",
                "question": "How do I use the washer and dryer?",
                "answer": "They are located in the designated area. Please check the posted instructions."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_ac_temperature",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "エアコンの温度を変更できますか？",
                "answer": "各部屋のリモコンで調整できます。外出時は電源を切ってください。"
            },
            {
                "language": "en",
                "question": "Can I change the air conditioner temperature?",
                "answer": "Yes, use the remote in your room and turn it off when leaving."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_wifi_connection",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "WiFiに接続できません。",
                "answer": "一度WiFiをオフにして再接続してください。"
            },
            {
                "language": "en",
                "question": "I cannot connect to WiFi.",
                "answer": "Please turn WiFi off and reconnect."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_wifi_speed",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "WiFiが遅いと感じます。",
                "answer": "混雑時間帯は速度が低下する場合があります。"
            },
            {
                "language": "en",
                "question": "The WiFi feels slow.",
                "answer": "Speed may decrease during busy hours."
            }
        ]
    },
    # Location (6 questions)
    {
        "category": "location",
        "intent_key": "location_convenience_store",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "近くにコンビニはありますか？",
                "answer": "徒歩数分の場所にあります。"
            },
            {
                "language": "en",
                "question": "Is there a convenience store nearby?",
                "answer": "Yes, within a few minutes on foot."
            }
        ]
    },
    {
        "category": "location",
        "intent_key": "location_restaurants_late",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "夜遅くまで営業している飲食店はありますか？",
                "answer": "近隣に数店舗あります。"
            },
            {
                "language": "en",
                "question": "Are there restaurants open late at night?",
                "answer": "Yes, there are several nearby."
            }
        ]
    },
    {
        "category": "location",
        "intent_key": "location_atm",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "ATMは近くにありますか？",
                "answer": "コンビニ内ATMが利用できます。"
            },
            {
                "language": "en",
                "question": "Is there an ATM nearby?",
                "answer": "Yes, ATMs are available at convenience stores."
            }
        ]
    },
    {
        "category": "location",
        "intent_key": "location_pharmacy",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "薬局やドラッグストアはありますか？",
                "answer": "徒歩圏内にあります。"
            },
            {
                "language": "en",
                "question": "Is there a pharmacy nearby?",
                "answer": "Yes, within walking distance."
            }
        ]
    },
    {
        "category": "location",
        "intent_key": "location_taxi",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "タクシーを利用したいです。",
                "answer": "配車アプリをご利用ください。"
            },
            {
                "language": "en",
                "question": "I want to use a taxi.",
                "answer": "Please use a taxi app."
            }
        ]
    },
    {
        "category": "location",
        "intent_key": "location_nearest_station",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "最寄り駅までの行き方を教えてください。",
                "answer": "館内マップをご確認ください。"
            },
            {
                "language": "en",
                "question": "How do I get to the nearest station?",
                "answer": "Please check the in-house map."
            }
        ]
    },
    # Trouble (8 questions)
    {
        "category": "trouble",
        "intent_key": "trouble_room_key_not_opening",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "部屋の鍵が開きません。",
                "answer": "差し込み直して再度お試しください。"
            },
            {
                "language": "en",
                "question": "I cannot open my room key.",
                "answer": "Please reinsert and try again."
            }
        ]
    },
    {
        "category": "trouble",
        "intent_key": "trouble_left_key_inside",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "鍵を部屋に置いたまま外に出ました。",
                "answer": "スタッフにご連絡ください。"
            },
            {
                "language": "en",
                "question": "I left my key inside the room.",
                "answer": "Please contact staff."
            }
        ]
    },
    {
        "category": "trouble",
        "intent_key": "trouble_no_water_hot_water",
        "priority": 5,
        "translations": [
            {
                "language": "ja",
                "question": "水やお湯が出ません。",
                "answer": "数分待っても改善しない場合はご連絡ください。"
            },
            {
                "language": "en",
                "question": "There is no water or hot water.",
                "answer": "Please contact us if it does not improve."
            }
        ]
    },
    {
        "category": "trouble",
        "intent_key": "trouble_lights_ac_not_working",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "照明やエアコンが動きません。",
                "answer": "ブレーカーを確認してください。"
            },
            {
                "language": "en",
                "question": "Lights or air conditioner do not work.",
                "answer": "Please check the breaker."
            }
        ]
    },
    {
        "category": "trouble",
        "intent_key": "trouble_other_guest_behavior",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "他のゲストの行動が気になります。",
                "answer": "直接注意せず、チャットでお知らせください。"
            },
            {
                "language": "en",
                "question": "Another guest is bothering me.",
                "answer": "Please inform us via chat instead of confronting them."
            }
        ]
    },
    {
        "category": "trouble",
        "intent_key": "trouble_feeling_unwell_not_emergency",
        "priority": 4,
        "translations": [
            {
                "language": "ja",
                "question": "体調が悪いが緊急ではありません。",
                "answer": "無理をせず休憩してください。"
            },
            {
                "language": "en",
                "question": "I feel unwell but it is not an emergency.",
                "answer": "Please rest and take care."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_online_meetings",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "オンライン会議は可能ですか？",
                "answer": "通常利用は可能ですが、高負荷通信は不安定になる場合があります。"
            },
            {
                "language": "en",
                "question": "Can I do online meetings?",
                "answer": "Yes, but high-bandwidth use may be unstable."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_power_adapters",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "変換プラグはありますか？",
                "answer": "数量限定で用意しています。"
            },
            {
                "language": "en",
                "question": "Do you have power plug adapters?",
                "answer": "Yes, a limited number are available."
            }
        ]
    }
]