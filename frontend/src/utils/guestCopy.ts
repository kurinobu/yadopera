/**
 * ゲスト画面（ウェルカム・緊急連絡先等）用の表示文言（多言語）
 * ゲストが選択した言語に応じて getGuestCopy(lang) で取得する。
 * 対応: ja, en, zh-TW, zh-CN, fr, es, ko, th（SUPPORTED_LANGUAGES と同一）。
 * 未対応の言語コードは en にフォールバック。
 */

export interface GuestCopy {
  emergency: {
    title: string
    ambulanceFire: string
    police: string
    facilityContact: string
  }
  topQuestions: {
    sectionTitle: string
    emptyMessage: string
  }
  messageInput: {
    label: string
    placeholder: string
  }
  facilityHeader: {
    checkIn: string
    checkOut: string
    loading: string
  }
}

const COPY_JA: GuestCopy = {
  emergency: {
    title: '緊急連絡先',
    ambulanceFire: '救急・消防',
    police: '警察',
    facilityContact: '施設連絡先'
  },
  topQuestions: {
    sectionTitle: 'よくある質問',
    emptyMessage: 'よくある質問はありません'
  },
  messageInput: {
    label: 'メッセージを入力',
    placeholder: '質問を入力してください...'
  },
  facilityHeader: {
    checkIn: 'チェックイン',
    checkOut: 'チェックアウト',
    loading: '読み込み中...'
  }
}

const COPY_EN: GuestCopy = {
  emergency: {
    title: 'Emergency Contact',
    ambulanceFire: 'Ambulance / Fire',
    police: 'Police',
    facilityContact: 'Facility contact'
  },
  topQuestions: {
    sectionTitle: 'Frequently Asked Questions',
    emptyMessage: 'No FAQs yet'
  },
  messageInput: {
    label: 'Enter your message',
    placeholder: 'Enter your question...'
  },
  facilityHeader: {
    checkIn: 'Check-in',
    checkOut: 'Check-out',
    loading: 'Loading...'
  }
}

/** 繁體中文 */
const COPY_ZH_TW: GuestCopy = {
  emergency: {
    title: '緊急聯絡方式',
    ambulanceFire: '救護・消防',
    police: '警察',
    facilityContact: '設施聯絡方式'
  },
  topQuestions: {
    sectionTitle: '常見問題',
    emptyMessage: '尚無常見問題'
  },
  messageInput: {
    label: '輸入訊息',
    placeholder: '請輸入問題...'
  },
  facilityHeader: {
    checkIn: '入住',
    checkOut: '退房',
    loading: '載入中...'
  }
}

/** 简体中文 */
const COPY_ZH_CN: GuestCopy = {
  emergency: {
    title: '紧急联系',
    ambulanceFire: '急救/消防',
    police: '警察',
    facilityContact: '设施联系'
  },
  topQuestions: {
    sectionTitle: '常见问题',
    emptyMessage: '暂无常见问题'
  },
  messageInput: {
    label: '输入消息',
    placeholder: '请输入您的问题...'
  },
  facilityHeader: {
    checkIn: '入住',
    checkOut: '退房',
    loading: '加载中...'
  }
}

/** Français */
const COPY_FR: GuestCopy = {
  emergency: {
    title: 'Urgences',
    ambulanceFire: 'Ambulance / Pompiers',
    police: 'Police',
    facilityContact: 'Contact établissement'
  },
  topQuestions: {
    sectionTitle: 'Questions fréquentes',
    emptyMessage: "Aucune FAQ pour l'instant"
  },
  messageInput: {
    label: 'Entrez votre message',
    placeholder: 'Posez votre question...'
  },
  facilityHeader: {
    checkIn: 'Arrivée',
    checkOut: 'Départ',
    loading: 'Chargement...'
  }
}

/** Español */
const COPY_ES: GuestCopy = {
  emergency: {
    title: 'Contacto de emergencia',
    ambulanceFire: 'Ambulancia / Bomberos',
    police: 'Policía',
    facilityContact: 'Contacto del alojamiento'
  },
  topQuestions: {
    sectionTitle: 'Preguntas frecuentes',
    emptyMessage: 'No hay preguntas frecuentes'
  },
  messageInput: {
    label: 'Introduzca su mensaje',
    placeholder: 'Escriba su pregunta...'
  },
  facilityHeader: {
    checkIn: 'Entrada',
    checkOut: 'Salida',
    loading: 'Cargando...'
  }
}

/** 한국어 */
const COPY_KO: GuestCopy = {
  emergency: {
    title: '긴급 연락처',
    ambulanceFire: '구급 / 소방',
    police: '경찰',
    facilityContact: '시설 연락처'
  },
  topQuestions: {
    sectionTitle: '자주 묻는 질문',
    emptyMessage: '등록된 FAQ가 없습니다'
  },
  messageInput: {
    label: '메시지 입력',
    placeholder: '질문을 입력해 주세요...'
  },
  facilityHeader: {
    checkIn: '체크인',
    checkOut: '체크아웃',
    loading: '로딩 중...'
  }
}

/** ไทย */
const COPY_TH: GuestCopy = {
  emergency: {
    title: 'ติดต่อฉุกเฉิน',
    ambulanceFire: 'แพทย์ฉุกเฉิน/ดับเพลิง',
    police: 'ตำรวจ',
    facilityContact: 'ติดต่อที่พัก'
  },
  topQuestions: {
    sectionTitle: 'คำถามที่พบบ่อย',
    emptyMessage: 'ยังไม่มีคำถามที่พบบ่อย'
  },
  messageInput: {
    label: 'ใส่ข้อความ',
    placeholder: 'กรอกคำถามของคุณ...'
  },
  facilityHeader: {
    checkIn: 'เช็คอิน',
    checkOut: 'เช็คเอาท์',
    loading: 'กำลังโหลด...'
  }
}

const COPY_MAP: Record<string, GuestCopy> = {
  ja: COPY_JA,
  en: COPY_EN,
  'zh-TW': COPY_ZH_TW,
  'zh-CN': COPY_ZH_CN,
  fr: COPY_FR,
  es: COPY_ES,
  ko: COPY_KO,
  th: COPY_TH
}

const FALLBACK_LANG = 'en'

/**
 * 指定言語のゲスト画面用文言を返す。未対応言語の場合は en にフォールバックする。
 */
export function getGuestCopy(lang: string): GuestCopy {
  const normalized = (lang || '').trim() || FALLBACK_LANG
  return COPY_MAP[normalized] ?? COPY_MAP[FALLBACK_LANG]
}
