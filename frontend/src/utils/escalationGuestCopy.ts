/**
 * ゲスト「スタッフに連絡」周りの表示文言（多言語）
 * 方針 A：お返事までの目安は全員同一の穏やかな固定文。
 */

export interface EscalationGuestStrings {
  staffContactButton: string
  confirmTitle: string
  /** 方針 A：目安の固定文 */
  policyLine: string
  /** 注意（緊急・即時でない旨） */
  cautionLine: string
  cancel: string
  submit: string
  sending: string
  successTitle: string
  /** 受付番号 n を含む本文 */
  successBody: (receiptNumber: number) => string
  close: string
  errFacility: string
  errSession: string
  errGeneric: string
  errConversationNotFound: string
  errSessionExpired: string
}

const STR_JA: EscalationGuestStrings = {
  staffContactButton: 'スタッフに連絡する',
  confirmTitle: 'スタッフへお知らせ',
  policyLine: 'お返事までにお時間をいただくことがあります。すぐにお返事できない場合もあります。',
  cautionLine:
    'お急ぎのときや緊急のときは、施設の案内に記載の電話番号など、必要な窓口へ連絡してください。この画面からのお知らせだけでは、すぐに駆けつけることはできません。',
  cancel: 'やめる',
  submit: '送信する',
  sending: '送信中…',
  successTitle: 'お知らせを受け付けました',
  successBody: (n) =>
    `お問い合わせを受け付けました。受付番号は ${n} です。この番号をスタッフにお伝えください。このあと、スタッフが内容を確認します。`,
  close: '閉じる',
  errFacility: '施設情報を読み込めませんでした。ページを開き直してからお試しください。',
  errSession: 'このチャットを続けることができません。ページを開き直してからお試しください。',
  errGeneric: '送信できませんでした。しばらくしてからもう一度お試しください。',
  errConversationNotFound:
    'まだ会話が始まっていないようです。メッセージを一度送ってから、もう一度お試しください。',
  errSessionExpired: 'このチャットの有効期限が切れています。ページを開き直してからお試しください。'
}

const STR_EN: EscalationGuestStrings = {
  staffContactButton: 'Contact staff',
  confirmTitle: 'Message staff',
  policyLine: 'We may need some time to reply. A quick response is not always possible.',
  cautionLine:
    'If it is urgent, please call the property using the phone number on the welcome page or other information you received. Sending a message here does not dispatch someone immediately.',
  cancel: 'Cancel',
  submit: 'Send',
  sending: 'Sending…',
  successTitle: 'Request received',
  successBody: (n) =>
    `We have received your request. Your reference number is ${n}. Please share this number with staff. Staff will review your message.`,
  close: 'Close',
  errFacility: 'We could not load the property information. Please refresh the page and try again.',
  errSession: 'We could not continue this chat. Please refresh the page and try again.',
  errGeneric: 'Something went wrong. Please try again in a moment.',
  errConversationNotFound: 'Please send a message first, then try contacting staff again.',
  errSessionExpired: 'This chat session has expired. Please refresh the page and try again.'
}

const STR_ZH_TW: EscalationGuestStrings = {
  staffContactButton: '聯絡工作人員',
  confirmTitle: '傳送給工作人員',
  policyLine: '回覆可能需要一些時間，無法保證立即回覆。',
  cautionLine:
    '如有急事或緊急狀況，請依照入住資料的電話等方式聯絡住宿方。僅在此留言並無法立刻派人處理。',
  cancel: '取消',
  submit: '送出',
  sending: '傳送中…',
  successTitle: '已收到通知',
  successBody: (n) => `我們已收到您的聯絡。受理編號為 ${n}。請將此編號提供給工作人員。工作人員將會檢視內容。`,
  close: '關閉',
  errFacility: '無法讀取住宿資訊。請重新整理頁面後再試。',
  errSession: '無法繼續此對話。請重新整理頁面後再試。',
  errGeneric: '無法送出。請稍後再試。',
  errConversationNotFound: '請先傳送一則訊息後，再試一次聯絡工作人員。',
  errSessionExpired: '此對話已失效。請重新整理頁面後再試。'
}

const STR_ZH_CN: EscalationGuestStrings = {
  staffContactButton: '联系工作人员',
  confirmTitle: '发送给工作人员',
  policyLine: '回复可能需要一些时间，无法保证立即回复。',
  cautionLine:
    '如有急事或紧急情况，请按入住说明中的电话等方式联系住宿方。仅在此留言无法立刻派人处理。',
  cancel: '取消',
  submit: '发送',
  sending: '发送中…',
  successTitle: '已收到',
  successBody: (n) => `我们已收到您的联络。受理编号为 ${n}。请将此编号提供给工作人员。工作人员将查看内容。`,
  close: '关闭',
  errFacility: '无法读取住宿信息。请刷新页面后重试。',
  errSession: '无法继续此对话。请刷新页面后重试。',
  errGeneric: '发送失败。请稍后重试。',
  errConversationNotFound: '请先发送一条消息，再尝试联系工作人员。',
  errSessionExpired: '此对话已过期。请刷新页面后重试。'
}

const STR_FR: EscalationGuestStrings = {
  staffContactButton: 'Contacter le personnel',
  confirmTitle: 'Envoyer au personnel',
  policyLine: 'Une réponse peut prendre du temps ; une réponse immédiate n’est pas garantie.',
  cautionLine:
    "En cas d'urgence, appelez l'établissement (numéro sur la page d'accueil ou documents). Ce message ne fait pas intervenir quelqu'un sur place immédiatement.",
  cancel: 'Annuler',
  submit: 'Envoyer',
  sending: 'Envoi…',
  successTitle: 'Demande reçue',
  successBody: (n) =>
    `Nous avons bien reçu votre message. Votre numéro de suivi est ${n}. Merci de communiquer ce numéro au personnel. Le personnel va le consulter.`,
  close: 'Fermer',
  errFacility: "Impossible de charger l'établissement. Actualisez la page et réessayez.",
  errSession: 'Impossible de continuer cette conversation. Actualisez la page et réessayez.',
  errGeneric: "Envoi impossible. Réessayez dans un instant.",
  errConversationNotFound: "Envoyez d'abord un message, puis réessayez.",
  errSessionExpired: 'Cette conversation a expiré. Actualisez la page et réessayez.'
}

const STR_ES: EscalationGuestStrings = {
  staffContactButton: 'Contactar al personal',
  confirmTitle: 'Enviar al personal',
  policyLine: 'La respuesta puede tardar; no siempre es inmediata.',
  cautionLine:
    'Si es urgente, llame al alojamiento (teléfono en la página de bienvenida o en la información que le dieron). Este mensaje no envía a nadie al momento.',
  cancel: 'Cancelar',
  submit: 'Enviar',
  sending: 'Enviando…',
  successTitle: 'Recibido',
  successBody: (n) =>
    `Hemos recibido su mensaje. Su número de referencia es ${n}. Comparta este número con el personal. El personal lo revisará.`,
  close: 'Cerrar',
  errFacility: 'No se pudo cargar el alojamiento. Actualice la página e inténtelo de nuevo.',
  errSession: 'No se puede continuar este chat. Actualice la página e inténtelo de nuevo.',
  errGeneric: 'No se pudo enviar. Inténtelo de nuevo más tarde.',
  errConversationNotFound: 'Primero envíe un mensaje y vuelva a intentarlo.',
  errSessionExpired: 'Esta conversación ha caducado. Actualice la página e inténtelo de nuevo.'
}

const STR_KO: EscalationGuestStrings = {
  staffContactButton: '직원에게 연락',
  confirmTitle: '직원에게 보내기',
  policyLine: '답변까지 시간이 걸릴 수 있으며, 즉시 답변이 어려울 수 있습니다.',
  cautionLine:
    '긴급한 경우 숙소 안내의 전화번호 등으로 연락해 주세요. 이 화면만으로는 바로 현장에 조치가 이루어지지 않습니다.',
  cancel: '취소',
  submit: '보내기',
  sending: '보내는 중…',
  successTitle: '접수되었습니다',
  successBody: (n) =>
    `문의가 접수되었습니다. 접수 번호는 ${n} 입니다. 이 번호를 직원에게 알려 주세요. 직원이 내용을 확인합니다.`,
  close: '닫기',
  errFacility: '숙소 정보를 불러올 수 없습니다. 페이지를 새로 고친 뒤 다시 시도해 주세요.',
  errSession: '이 대화를 계속할 수 없습니다. 페이지를 새로 고친 뒤 다시 시도해 주세요.',
  errGeneric: '전송하지 못했습니다. 잠시 후 다시 시도해 주세요.',
  errConversationNotFound: '먼저 메시지를 보낸 뒤 다시 시도해 주세요.',
  errSessionExpired: '대화가 만료되었습니다. 페이지를 새로 고친 뒤 다시 시도해 주세요.'
}

const STR_TH: EscalationGuestStrings = {
  staffContactButton: 'ติดต่อเจ้าหน้าที่',
  confirmTitle: 'ส่งถึงเจ้าหน้าที่',
  policyLine: 'การตอบกลับอาจใช้เวลา และอาจไม่ทันที',
  cautionLine:
    'หากเป็นกรณีเร่งด่วน โปรดโทรติดต่อที่พักตามหมายเลขในหน้าต้อนรับหรือเอกสารที่ได้รับ การส่งข้อความที่นี่ไม่ได้หมายความว่ามีคนมาถึงทันที',
  cancel: 'ยกเลิก',
  submit: 'ส่ง',
  sending: 'กำลังส่ง…',
  successTitle: 'รับเรื่องแล้ว',
  successBody: (n) => `เราได้รับคำขอของคุณแล้ว หมายเลขอ้างอิงคือ ${n} โปรดแจ้งหมายเลขนี้กับเจ้าหน้าที่ เจ้าหน้าที่จะตรวจสอบข้อความ`,
  close: 'ปิด',
  errFacility: 'โหลดข้อมูลที่พักไม่ได้ กรุณารีเฟรชแล้วลองอีกครั้ง',
  errSession: 'ดำเนินการแชทต่อไม่ได้ กรุณารีเฟรชแล้วลองอีกครั้ง',
  errGeneric: 'ส่งไม่สำเร็จ กรุณาลองใหม่ภายหลัง',
  errConversationNotFound: 'กรุณาส่งข้อความก่อน แล้วลองติดต่อเจ้าหน้าที่อีกครั้ง',
  errSessionExpired: 'แชทนี้หมดอายุแล้ว กรุณารีเฟรชแล้วลองอีกครั้ง'
}

const MAP: Record<string, EscalationGuestStrings> = {
  ja: STR_JA,
  en: STR_EN,
  'zh-TW': STR_ZH_TW,
  'zh-CN': STR_ZH_CN,
  fr: STR_FR,
  es: STR_ES,
  ko: STR_KO,
  th: STR_TH
}

export function getEscalationGuestCopy(lang: string): EscalationGuestStrings {
  const key = (lang || '').trim() || 'en'
  return MAP[key] ?? STR_EN
}
