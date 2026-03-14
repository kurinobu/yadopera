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
            },
            {
                "language": "zh-TW",
                "question": "晚上有安靜規定嗎？",
                "answer": "晚上10點後請您盡量保持安靜。請在公共區域講電話或交談。"
            },
            {
                "language": "fr",
                "question": "Y a-t-il des règles de calme la nuit ?",
                "answer": "Veuillez garder le silence après 22h00. Les appels et conversations doivent se faire dans les espaces communs."
            },
            {
                "language": "ko",
                "question": "밤에 정숙 규칙이 있나요?",
                "answer": "오후 10시 이후에는 조용히 해 주세요. 전화나 대화는 공용 공간에서 해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "晚上有安静规定吗？",
                "answer": "晚上10点后请尽量保持安静。请在公共区域打电话或交谈。"
            },
            {
                "language": "es",
                "question": "¿Hay reglas de silencio por la noche?",
                "answer": "Por favor mantenga el silencio después de las 22:00. Las llamadas y conversaciones deben realizarse en las zonas comunes."
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
            },
            {
                "language": "zh-TW",
                "question": "請問館內吸菸規定？",
                "answer": "建築物內全面禁菸。請您使用指定的室外吸菸區。"
            },
            {
                "language": "fr",
                "question": "Quelle est la politique en matière de tabac ?",
                "answer": "Il est interdit de fumer dans le bâtiment. Veuillez utiliser l'espace fumeurs à l'extérieur."
            },
            {
                "language": "ko",
                "question": "흡연 규정이 어떻게 되나요?",
                "answer": "건물 내부는 금연입니다. 지정된 야외 흡연 구역을 이용해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "馆内吸烟规定是什么？",
                "answer": "建筑物内全面禁烟。请使用指定的室外吸烟区。"
            },
            {
                "language": "es",
                "question": "¿Cuál es la política de fumadores?",
                "answer": "Está prohibido fumar dentro del edificio. Por favor use la zona de fumadores al aire libre."
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
                "answer": "宿泊中のゲストであれば自由に利用できます。長時間の占有はご遠慮ください。共有スペースで寝ないでください。"
            },
            {
                "language": "en",
                "question": "Can anyone use the common areas?",
                "answer": "All staying guests may use them freely. Please avoid occupying them for long periods. Do not sleep in common areas."
            },
            {
                "language": "zh-TW",
                "question": "共用區域誰都可以使用嗎？",
                "answer": "住宿中的房客均可自由使用。請勿長時間佔用。請勿在共用區域就寢。"
            },
            {
                "language": "fr",
                "question": "Les espaces communs sont-ils accessibles à tous ?",
                "answer": "Tous les clients peuvent les utiliser librement. Veuillez éviter de les occuper longtemps. Ne dormez pas dans les espaces communs."
            },
            {
                "language": "ko",
                "question": "공용 공간은 누구나 사용할 수 있나요?",
                "answer": "투숙객이라면 자유롭게 이용하실 수 있습니다. 장시간 독점 사용은 자제해 주세요. 공용 공간에서 취침하지 마세요."
            },
            {
                "language": "zh-CN",
                "question": "共用空间谁都可以使用吗？",
                "answer": "住宿中的客人均可自由使用。请勿长时间占用。请勿在共用区域就寝。"
            },
            {
                "language": "es",
                "question": "¿Puede cualquiera usar las zonas comunes?",
                "answer": "Todos los huéspedes pueden usarlas libremente. Evite ocuparlas durante mucho tiempo. No duerma en las zonas comunes."
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
            },
            {
                "language": "zh-TW",
                "question": "可以進入其他房客的房間嗎？",
                "answer": "基於安全考量，禁止進入其他房客的房間。"
            },
            {
                "language": "fr",
                "question": "Puis-je entrer dans la chambre d'un autre client ?",
                "answer": "Pour des raisons de sécurité, l'accès aux chambres des autres clients est interdit."
            },
            {
                "language": "ko",
                "question": "다른 투숙객 방에 들어가도 되나요?",
                "answer": "보안상 다른 투숙객의 방 출입은 금지되어 있습니다."
            },
            {
                "language": "zh-CN",
                "question": "可以进入其他客人的房间吗？",
                "answer": "出于安全考虑，禁止进入其他客人的房间。"
            },
            {
                "language": "es",
                "question": "¿Puedo entrar en la habitación de otro huésped?",
                "answer": "Por razones de seguridad, no está permitido entrar en las habitaciones de otros huéspedes."
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
                "answer": "節度を守っていただければ可能です。騒音や迷惑行為は禁止です。ベッドでは飲まないでください。"
            },
            {
                "language": "en",
                "question": "Is drinking alcohol allowed inside the property?",
                "answer": "Yes, as long as it is done responsibly. Please avoid noise or disturbing behavior. Do not drink in bed."
            },
            {
                "language": "zh-TW",
                "question": "館內可以飲酒嗎？",
                "answer": "可以，請適量並自律。請勿喧嘩或造成他人困擾。請勿在床上飲酒。"
            },
            {
                "language": "fr",
                "question": "La consommation d'alcool est-elle autorisée ?",
                "answer": "Oui, avec modération. Veuillez éviter le bruit et les comportements gênants. Ne buvez pas au lit."
            },
            {
                "language": "ko",
                "question": "숙소 안에서 음주해도 되나요?",
                "answer": "네, 절도 있게 드시면 됩니다. 소음이나 다른 분께 불편을 주는 행위는 자제해 주세요. 침대에서는 음주하지 마세요."
            },
            {
                "language": "zh-CN",
                "question": "馆内可以饮酒吗？",
                "answer": "可以，请适量并自律。请勿喧哗或造成他人困扰。请勿在床上饮酒。"
            },
            {
                "language": "es",
                "question": "¿Se puede consumir alcohol en el alojamiento?",
                "answer": "Sí, con moderación. Evite el ruido y las conductas molestas. No beba en la cama."
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
            },
            {
                "language": "zh-TW",
                "question": "住宿期間如何聯絡？",
                "answer": "住宿期間請您使用此聊天功能。退房後無法提供支援。"
            },
            {
                "language": "fr",
                "question": "Comment vous contacter pendant mon séjour ?",
                "answer": "Veuillez utiliser ce chat pendant votre séjour. Le support n'est pas disponible après le départ."
            },
            {
                "language": "ko",
                "question": "숙박 중 문의는 어떻게 하나요?",
                "answer": "숙박 중에는 이 채팅을 이용해 주세요. 체크아웃 후에는 지원이 불가합니다."
            },
            {
                "language": "zh-CN",
                "question": "住宿期间如何联系？",
                "answer": "住宿期间请使用此聊天功能。退房后无法提供支持。"
            },
            {
                "language": "es",
                "question": "¿Cómo puedo contactar durante mi estancia?",
                "answer": "Por favor use este chat durante su estancia. No hay soporte después del check-out."
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
            },
            {
                "language": "zh-TW",
                "question": "退房前需要做什麼？",
                "answer": "請您收拾個人物品、處理垃圾，並歸還借用備品。"
            },
            {
                "language": "fr",
                "question": "Que dois-je faire avant le départ ?",
                "answer": "Veuillez récupérer vos affaires, jeter les déchets et rendre les articles fournis."
            },
            {
                "language": "ko",
                "question": "체크아웃 전에 무엇을 해야 하나요?",
                "answer": "개인 소지품을 챙기시고, 쓰레기를 처리하시며, 빌려 쓰신 비품을 반납해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "退房前需要做什么？",
                "answer": "请收拾个人物品、处理垃圾，并归还借用备品。"
            },
            {
                "language": "es",
                "question": "¿Qué debo hacer antes del check-out?",
                "answer": "Recoja sus pertenencias, deseche la basura y devuelva los artículos proporcionados."
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
            },
            {
                "language": "zh-TW",
                "question": "床單和浴巾要還到哪裡？",
                "answer": "請您於退房前將床單與枕頭套放入大廳紅色回收箱，浴巾放入藍色回收箱。"
            },
            {
                "language": "fr",
                "question": "Où dois-je déposer les draps et serviettes ?",
                "answer": "Veuillez déposer draps et taies dans la boîte rouge au lobby, et les serviettes dans la boîte bleue avant le départ."
            },
            {
                "language": "ko",
                "question": "침구류와 수건은 어디에 반납하나요?",
                "answer": "체크아웃 전에 침구류와 베개커버는 로비 빨간 수거함에, 목욕 수건은 파란 수거함에 넣어 주세요."
            },
            {
                "language": "zh-CN",
                "question": "床单和浴巾要还到哪里？",
                "answer": "请您于退房前将床单与枕头套放入大厅红色回收箱，浴巾放入蓝色回收箱。"
            },
            {
                "language": "es",
                "question": "¿Dónde devuelvo las sábanas y toallas?",
                "answer": "Deposite sábanas y fundas en la caja roja del lobby, y las toallas en la caja azul antes del check-out."
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
            },
            {
                "language": "zh-TW",
                "question": "淋浴隨時可以使用嗎？",
                "answer": "24小時均可使用。使用後請您換氣並簡單清潔。"
            },
            {
                "language": "fr",
                "question": "Puis-je utiliser la douche à tout moment ?",
                "answer": "Oui, les douches sont disponibles 24h/24. Veuillez aérer et nettoyer après utilisation."
            },
            {
                "language": "ko",
                "question": "샤워는 언제든 사용할 수 있나요?",
                "answer": "24시간 이용 가능합니다. 사용 후 환기와 간단한 정리를 부탁드립니다."
            },
            {
                "language": "zh-CN",
                "question": "淋浴随时可以使用吗？",
                "answer": "24小时均可使用。使用后请通风并简单清洁。"
            },
            {
                "language": "es",
                "question": "¿Puedo usar la ducha en cualquier momento?",
                "answer": "Sí, las duchas están disponibles 24 horas. Por favor ventile y limpie después de usar."
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
            },
            {
                "language": "zh-TW",
                "question": "吹風機在哪裡？",
                "answer": "洗面區的架子上。使用後請您放回原處。"
            },
            {
                "language": "fr",
                "question": "Où se trouve le sèche-cheveux ?",
                "answer": "Sur les étagères dans l'espace lavabo. Veuillez le remettre après usage."
            },
            {
                "language": "ko",
                "question": "드라이어는 어디에 있나요?",
                "answer": "세면대 구역 선반에 있습니다. 사용 후 제자리에 놓아 주세요."
            },
            {
                "language": "zh-CN",
                "question": "吹风机在哪里？",
                "answer": "在洗脸区的架子上。使用后请放回原处。"
            },
            {
                "language": "es",
                "question": "¿Dónde está el secador de pelo?",
                "answer": "En las estanterías del área del lavabo. Por favor devuélvalo después de usar."
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
                "answer": "使用可能です。利用後は必ず清掃し、調理器具を洗浄し元の場所に戻してください。"
            },
            {
                "language": "en",
                "question": "Can I use the shared kitchen?",
                "answer": "Yes. Please clean after use, wash utensils, and return them to their original places."
            },
            {
                "language": "zh-TW",
                "question": "共用廚房可以使用嗎？",
                "answer": "可以。使用後請您清潔、洗淨廚具並歸位。"
            },
            {
                "language": "fr",
                "question": "Puis-je utiliser la cuisine commune ?",
                "answer": "Oui. Veuillez nettoyer après usage, laver les ustensiles et les remettre à leur place."
            },
            {
                "language": "ko",
                "question": "공용 주방을 사용해도 되나요?",
                "answer": "네. 사용 후 청소하시고 조리 도구를 세척한 뒤 제자리에 놓아 주세요."
            },
            {
                "language": "zh-CN",
                "question": "共用厨房可以使用吗？",
                "answer": "可以。使用后请清洁、洗净厨具并归位。"
            },
            {
                "language": "es",
                "question": "¿Puedo usar la cocina compartida?",
                "answer": "Sí. Por favor limpie después de usar, lave los utensilios y devuélvalos a su lugar."
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
                "answer": "共用冷蔵庫を利用できます。名前と日付を記入してください。チェックアウト前には処分してください。"
            },
            {
                "language": "en",
                "question": "Can I store items in the refrigerator?",
                "answer": "Yes, please label your items with your name and date. Please dispose of them before checkout."
            },
            {
                "language": "zh-TW",
                "question": "冰箱可以放東西嗎？",
                "answer": "可以，請標註姓名與日期。退房前請處理完畢。"
            },
            {
                "language": "fr",
                "question": "Puis-je mettre des aliments au réfrigérateur ?",
                "answer": "Oui, veuillez étiqueter vos affaires avec votre nom et la date. Veuillez les retirer avant le départ."
            },
            {
                "language": "ko",
                "question": "냉장고에 음식을 넣어도 되나요?",
                "answer": "네. 이름과 날짜를 적어 주세요. 체크아웃 전에 처리해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "冰箱可以放东西吗？",
                "answer": "可以，请标注姓名与日期。退房前请处理完毕。"
            },
            {
                "language": "es",
                "question": "¿Puedo guardar cosas en el refrigerador?",
                "answer": "Sí, por favor etiquete sus artículos con nombre y fecha. Por favor retírelos antes del checkout."
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
                "answer": "指定エリアにあります。現金のコインしか使えません。料金と操作方法は掲示をご確認ください。"
            },
            {
                "language": "en",
                "question": "How do I use the washer and dryer?",
                "answer": "They are in the designated area. Only cash coins are accepted. Please check the posted instructions for fees and operation."
            },
            {
                "language": "zh-TW",
                "question": "洗衣機和烘乾機怎麼用？",
                "answer": "在指定區域。僅接受現金硬幣。請參閱現場張貼的使用說明。"
            },
            {
                "language": "fr",
                "question": "Comment utiliser la machine à laver et le sèche-linge ?",
                "answer": "Ils sont dans l'espace indiqué. Seules les pièces sont acceptées. Consultez les instructions affichées."
            },
            {
                "language": "ko",
                "question": "세탁기와 건조기 사용 방법을 알려주세요.",
                "answer": "지정된 구역에 있습니다. 현금 동전만 사용 가능합니다. 게시된 이용 안내를 확인해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "洗衣机和烘干机怎么用？",
                "answer": "在指定区域。仅接受现金硬币。请参阅现场张贴的使用说明。"
            },
            {
                "language": "es",
                "question": "¿Cómo uso la lavadora y la secadora?",
                "answer": "Están en la zona indicada. Solo se aceptan monedas. Consulte las instrucciones publicadas."
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
            },
            {
                "language": "zh-TW",
                "question": "可以調整冷氣溫度嗎？",
                "answer": "請您使用房內遙控器。外出時請關閉電源。"
            },
            {
                "language": "fr",
                "question": "Puis-je régler la climatisation ?",
                "answer": "Oui, utilisez la télécommande dans votre chambre et éteignez en partant."
            },
            {
                "language": "ko",
                "question": "에어컨 온도를 바꿀 수 있나요?",
                "answer": "객실 리모컨으로 조절하실 수 있습니다. 외출 시에는 전원을 꺼 주세요."
            },
            {
                "language": "zh-CN",
                "question": "可以调整空调温度吗？",
                "answer": "请使用房内遥控器。外出时请关闭电源。"
            },
            {
                "language": "es",
                "question": "¿Puedo cambiar la temperatura del aire acondicionado?",
                "answer": "Sí, use el mando a distancia de su habitación y apáguelo al salir."
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
            },
            {
                "language": "zh-TW",
                "question": "無法連上WiFi。",
                "answer": "請您先關閉WiFi後重新連線。"
            },
            {
                "language": "fr",
                "question": "Je n'arrive pas à me connecter au WiFi.",
                "answer": "Veuillez désactiver le WiFi puis vous reconnecter."
            },
            {
                "language": "ko",
                "question": "WiFi에 연결되지 않아요.",
                "answer": "WiFi를 끄고 다시 연결해 보세요."
            },
            {
                "language": "zh-CN",
                "question": "无法连上WiFi。",
                "answer": "请先关闭WiFi后重新连接。"
            },
            {
                "language": "es",
                "question": "No puedo conectarme al WiFi.",
                "answer": "Por favor apague el WiFi y vuelva a conectarse."
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
            },
            {
                "language": "zh-TW",
                "question": "WiFi很慢。",
                "answer": "尖峰時段可能較慢。"
            },
            {
                "language": "fr",
                "question": "Le WiFi est lent.",
                "answer": "La vitesse peut baisser aux heures de pointe."
            },
            {
                "language": "ko",
                "question": "WiFi가 느려요.",
                "answer": "이용이 많은 시간대에는 속도가 떨어질 수 있습니다."
            },
            {
                "language": "zh-CN",
                "question": "WiFi很慢。",
                "answer": "高峰时段可能较慢。"
            },
            {
                "language": "es",
                "question": "El WiFi va lento.",
                "answer": "La velocidad puede disminuir en horas punta."
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
            },
            {
                "language": "zh-TW",
                "question": "附近有便利商店嗎？",
                "answer": "步行數分鐘內有。"
            },
            {
                "language": "fr",
                "question": "Y a-t-il un convenience store à proximité ?",
                "answer": "Oui, à quelques minutes à pied."
            },
            {
                "language": "ko",
                "question": "근처에 편의점이 있나요?",
                "answer": "도보로 몇 분 거리에 있습니다."
            },
            {
                "language": "zh-CN",
                "question": "附近有便利店吗？",
                "answer": "步行数分钟内有。"
            },
            {
                "language": "es",
                "question": "¿Hay una tienda de conveniencia cerca?",
                "answer": "Sí, a pocos minutos a pie."
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
            },
            {
                "language": "zh-TW",
                "question": "有營業到深夜的餐廳嗎？",
                "answer": "附近有幾家。"
            },
            {
                "language": "fr",
                "question": "Y a-t-il des restaurants ouverts tard le soir ?",
                "answer": "Oui, plusieurs à proximité."
            },
            {
                "language": "ko",
                "question": "밤늦게까지 하는 식당이 있나요?",
                "answer": "근처에 몇 군데 있습니다."
            },
            {
                "language": "zh-CN",
                "question": "有营业到深夜的餐厅吗？",
                "answer": "附近有几家。"
            },
            {
                "language": "es",
                "question": "¿Hay restaurantes abiertos hasta tarde?",
                "answer": "Sí, hay varios cerca."
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
            },
            {
                "language": "zh-TW",
                "question": "附近有ATM嗎？",
                "answer": "便利商店內有提款機。"
            },
            {
                "language": "fr",
                "question": "Y a-t-il un distributeur à proximité ?",
                "answer": "Oui, dans les convenience stores."
            },
            {
                "language": "ko",
                "question": "근처에 ATM이 있나요?",
                "answer": "편의점 내 ATM을 이용하실 수 있습니다."
            },
            {
                "language": "zh-CN",
                "question": "附近有ATM吗？",
                "answer": "便利店内有取款机。"
            },
            {
                "language": "es",
                "question": "¿Hay un cajero automático cerca?",
                "answer": "Sí, hay cajeros en las tiendas de conveniencia."
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
            },
            {
                "language": "zh-TW",
                "question": "附近有藥局或藥妝店嗎？",
                "answer": "步行可達。"
            },
            {
                "language": "fr",
                "question": "Y a-t-il une pharmacie à proximité ?",
                "answer": "Oui, à distance de marche."
            },
            {
                "language": "ko",
                "question": "근처에 약국이 있나요?",
                "answer": "도보 권 내에 있습니다."
            },
            {
                "language": "zh-CN",
                "question": "附近有药店吗？",
                "answer": "步行可达。"
            },
            {
                "language": "es",
                "question": "¿Hay una farmacia cerca?",
                "answer": "Sí, a distancia a pie."
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
            },
            {
                "language": "zh-TW",
                "question": "想叫計程車。",
                "answer": "請您使用叫車App。"
            },
            {
                "language": "fr",
                "question": "Je voudrais prendre un taxi.",
                "answer": "Veuillez utiliser une application de réservation."
            },
            {
                "language": "ko",
                "question": "택시를 이용하고 싶어요.",
                "answer": "택시 앱을 이용해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "想叫出租车。",
                "answer": "请使用叫车App。"
            },
            {
                "language": "es",
                "question": "Quiero usar un taxi.",
                "answer": "Por favor use una aplicación de reserva de taxis."
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
            },
            {
                "language": "zh-TW",
                "question": "最近車站怎麼走？",
                "answer": "請您參考館內地圖。"
            },
            {
                "language": "fr",
                "question": "Comment aller à la gare la plus proche ?",
                "answer": "Veuillez consulter le plan dans l'établissement."
            },
            {
                "language": "ko",
                "question": "가장 가까운 역까지 어떻게 가나요?",
                "answer": "숙소 내 안내도를 확인해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "最近车站怎么走？",
                "answer": "请参考馆内地图。"
            },
            {
                "language": "es",
                "question": "¿Cómo llego a la estación más cercana?",
                "answer": "Por favor consulte el plano del alojamiento."
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
            },
            {
                "language": "zh-TW",
                "question": "房門鑰匙打不開。",
                "answer": "請您重新插入後再試一次。"
            },
            {
                "language": "fr",
                "question": "Ma clé ne ouvre pas la porte.",
                "answer": "Veuillez la réinsérer et réessayer."
            },
            {
                "language": "ko",
                "question": "방 열쇠가 안 열려요.",
                "answer": "다시 꽂았다가 한 번 더 시도해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "房门钥匙打不开。",
                "answer": "请重新插入后再试一次。"
            },
            {
                "language": "es",
                "question": "No puedo abrir la llave de la habitación.",
                "answer": "Por favor vuelva a insertarla e intente de nuevo."
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
            },
            {
                "language": "zh-TW",
                "question": "鑰匙忘在房裡就出來了。",
                "answer": "請您聯絡工作人員。"
            },
            {
                "language": "fr",
                "question": "J'ai laissé ma clé dans la chambre.",
                "answer": "Veuillez contacter le personnel."
            },
            {
                "language": "ko",
                "question": "열쇠를 방에 두고 나왔어요.",
                "answer": "스태프에게 연락해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "钥匙忘在房里就出来了。",
                "answer": "请联系工作人员。"
            },
            {
                "language": "es",
                "question": "Dejé la llave dentro de la habitación.",
                "answer": "Por favor contacte al personal."
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
                "answer": "数分待っても改善しない場合はスタッフにご連絡ください。"
            },
            {
                "language": "en",
                "question": "There is no water or hot water.",
                "answer": "Please contact staff if it does not improve after a few minutes."
            },
            {
                "language": "zh-TW",
                "question": "沒有水或熱水。",
                "answer": "稍等數分鐘仍無改善請聯絡工作人員。"
            },
            {
                "language": "fr",
                "question": "Il n'y a pas d'eau ou d'eau chaude.",
                "answer": "Veuillez contacter le personnel si cela ne s'améliore pas après quelques minutes."
            },
            {
                "language": "ko",
                "question": "물이나 뜨거운 물이 안 나와요.",
                "answer": "몇 분 기다려도 나오지 않으면 스태프에게 연락해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "没有水或热水。",
                "answer": "稍等数分钟仍无改善请联系工作人员。"
            },
            {
                "language": "es",
                "question": "No hay agua ni agua caliente.",
                "answer": "Por favor contacte al personal si no mejora en unos minutos."
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
                "answer": "ブレーカーを確認してください。改善しない場合はスタッフにご連絡ください。"
            },
            {
                "language": "en",
                "question": "Lights or air conditioner do not work.",
                "answer": "Please check the breaker. If the issue persists, contact staff."
            },
            {
                "language": "zh-TW",
                "question": "燈或冷氣不運作。",
                "answer": "請您檢查斷路器。若仍無法改善請聯絡工作人員。"
            },
            {
                "language": "fr",
                "question": "Les lumières ou la climatisation ne fonctionnent pas.",
                "answer": "Veuillez vérifier le disjoncteur. Si le problème persiste, contactez le personnel."
            },
            {
                "language": "ko",
                "question": "조명이나 에어컨이 작동하지 않아요.",
                "answer": "차단기를 확인해 주세요. 그래도 해결되지 않으면 스태프에게 연락해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "灯或空调不运作。",
                "answer": "请检查断路器。若仍无法改善请联系工作人员。"
            },
            {
                "language": "es",
                "question": "Las luces o el aire acondicionado no funcionan.",
                "answer": "Por favor revise el interruptor automático. Si persiste, contacte al personal."
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
                "answer": "直接注意せず、スタッフにお知らせください。"
            },
            {
                "language": "en",
                "question": "Another guest is bothering me.",
                "answer": "Please inform staff instead of confronting them directly."
            },
            {
                "language": "zh-TW",
                "question": "其他房客的行為讓我不舒服。",
                "answer": "請勿直接衝突，請告知工作人員。"
            },
            {
                "language": "fr",
                "question": "Un autre client me dérange.",
                "answer": "Veuillez en informer le personnel plutôt que de le confronter."
            },
            {
                "language": "ko",
                "question": "다른 투숙객 행동이 신경 쓰여요.",
                "answer": "직접 말씀하지 마시고 스태프에게 알려 주세요."
            },
            {
                "language": "zh-CN",
                "question": "其他客人的行为让我不舒服。",
                "answer": "请勿直接冲突，请告知工作人员。"
            },
            {
                "language": "es",
                "question": "Otro huésped me molesta.",
                "answer": "Por favor informe al personal en lugar de confrontarlo."
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
                "answer": "無理をせず休憩してください。近所のドラッグストアで薬が販売されてます。"
            },
            {
                "language": "en",
                "question": "I feel unwell but it is not an emergency.",
                "answer": "Please rest. Medicine is available at nearby drugstores."
            },
            {
                "language": "zh-TW",
                "question": "身體不適但不是緊急狀況。",
                "answer": "請多休息。附近藥局或藥妝店有販售成藥。"
            },
            {
                "language": "fr",
                "question": "Je ne me sens pas bien mais ce n'est pas urgent.",
                "answer": "Veuillez vous reposer. Des médicaments sont en vente en pharmacie à proximité."
            },
            {
                "language": "ko",
                "question": "몸이 안 좋은데 급한 건 아니에요.",
                "answer": "무리하지 마시고 푹 쉬세요. 근처 드럭스토어에서 약을 구매하실 수 있습니다."
            },
            {
                "language": "zh-CN",
                "question": "身体不适但不是紧急状况。",
                "answer": "请多休息。附近药店有售非处方药。"
            },
            {
                "language": "es",
                "question": "Me siento mal pero no es una emergencia.",
                "answer": "Por favor descanse. Hay medicamentos en farmacias cercanas."
            }
        ]
    },
    {
        "category": "facilities",
        "intent_key": "facilities_bicycle_rental",
        "priority": 3,
        "translations": [
            {
                "language": "ja",
                "question": "自転車の貸し出しはありますか？",
                "answer": "有料で貸し出ししています。予約が必要です。スタッフに申し込んでください。"
            },
            {
                "language": "en",
                "question": "Do you offer bicycle rental?",
                "answer": "Yes, we rent bicycles for a fee. Reservation is required. Please ask staff to book."
            },
            {
                "language": "zh-TW",
                "question": "有腳踏車可以租借嗎？",
                "answer": "有付費租借服務，需事先預約。請向工作人員申辦。"
            },
            {
                "language": "fr",
                "question": "Proposez-vous la location de vélos ?",
                "answer": "Oui, location payante. Réservation requise. Veuillez vous adresser au personnel."
            },
            {
                "language": "ko",
                "question": "자전거 대여가 있나요?",
                "answer": "유료로 대여하고 있습니다. 예약이 필요합니다. 스태프에게 신청해 주세요."
            },
            {
                "language": "zh-CN",
                "question": "可以租借自行车吗？",
                "answer": "提供付费租借，需提前预约。请向工作人员申请。"
            },
            {
                "language": "es",
                "question": "¿Tienen alquiler de bicicletas?",
                "answer": "Sí, alquiler de pago. Se requiere reserva. Por favor solicite al personal."
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
                "answer": "数量限定で貸し出しています。"
            },
            {
                "language": "en",
                "question": "Do you have power plug adapters?",
                "answer": "Yes, we lend a limited number."
            },
            {
                "language": "zh-TW",
                "question": "有轉接插頭嗎？",
                "answer": "數量有限，可向我們租借。"
            },
            {
                "language": "fr",
                "question": "Avez-vous des adaptateurs de prise ?",
                "answer": "Oui, nous en prêtons en nombre limité."
            },
            {
                "language": "ko",
                "question": "변환 플러그 있나요?",
                "answer": "수량 한정으로 대여해 드립니다."
            },
            {
                "language": "zh-CN",
                "question": "有转换插头吗？",
                "answer": "数量有限，可向我们租借。"
            },
            {
                "language": "es",
                "question": "¿Tienen adaptadores de enchufe?",
                "answer": "Sí, prestamos un número limitado."
            }
        ]
    }
]