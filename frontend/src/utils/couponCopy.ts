/**
 * 固定フッター・クーポンエントリーモーダル用の表示文言（多言語）
 * ゲストが選択した言語に応じて getCouponCopy(lang) で取得する。
 * 対応: ja, en, zh-TW, fr, es, de, ko, th, vi（SUPPORTED_LANGUAGES と同一）。
 * 未対応の言語コードは en にフォールバック。
 */

export interface CouponCopy {
  couponButton: string
  modalTitle: string
  successTitle: string
  successDescription: string
  closeButton: string
  introText: string
  privacyNote: string
  labelName: string
  labelEmail: string
  placeholderName: string
  placeholderEmail: string
  cancelButton: string
  submitButton: string
  submittingButton: string
  errorSendFailed: string
}

const COPY_JA: CouponCopy = {
  couponButton: 'オトクなクーポン',
  modalTitle: 'オトクなクーポンを受け取る',
  successTitle: 'クーポンを送信しました。',
  successDescription: 'ご登録のメールアドレスにクーポンを送信しました。ご確認ください。',
  closeButton: '閉じる',
  introText: '次回のご予約でご利用いただけるクーポンをお送りします。メールアドレスをご入力ください。',
  privacyNote: '利用目的：次回予約のご案内のため。プライバシーポリシーに同意のうえ送信してください。',
  labelName: 'お名前（任意）',
  labelEmail: 'メールアドレス',
  placeholderName: '山田 太郎',
  placeholderEmail: 'example@email.com',
  cancelButton: 'キャンセル',
  submitButton: 'クーポンを受け取る',
  submittingButton: '送信中...',
  errorSendFailed: '送信に失敗しました。しばらくしてから再度お試しください。'
}

const COPY_EN: CouponCopy = {
  couponButton: 'Special Coupon',
  modalTitle: 'Get a special coupon',
  successTitle: 'Coupon sent.',
  successDescription: 'We have sent the coupon to your email address. Please check your inbox.',
  closeButton: 'Close',
  introText: 'We will send you a coupon for your next stay. Please enter your email address.',
  privacyNote: 'Purpose: To send you booking information. By submitting, you agree to our privacy policy.',
  labelName: 'Name (optional)',
  labelEmail: 'Email address',
  placeholderName: 'John Doe',
  placeholderEmail: 'example@email.com',
  cancelButton: 'Cancel',
  submitButton: 'Get coupon',
  submittingButton: 'Sending...',
  errorSendFailed: 'Failed to send. Please try again later.'
}

/** 繁體中文 */
const COPY_ZH_TW: CouponCopy = {
  couponButton: '優惠券',
  modalTitle: '領取優惠券',
  successTitle: '已發送優惠券。',
  successDescription: '我們已將優惠券發送至您的電子信箱，請查收。',
  closeButton: '關閉',
  introText: '我們將為您發送下次住宿可使用的優惠券，請輸入您的電子信箱。',
  privacyNote: '用途：寄送預約相關資訊。送出即表示同意我們的隱私權政策。',
  labelName: '姓名（選填）',
  labelEmail: '電子信箱',
  placeholderName: '王小明',
  placeholderEmail: 'example@email.com',
  cancelButton: '取消',
  submitButton: '領取優惠券',
  submittingButton: '發送中...',
  errorSendFailed: '發送失敗，請稍後再試。'
}

/** Français */
const COPY_FR: CouponCopy = {
  couponButton: 'Bon de réduction',
  modalTitle: 'Obtenir un bon de réduction',
  successTitle: 'Bon envoyé.',
  successDescription: 'Nous avons envoyé le bon à votre adresse e-mail. Veuillez vérifier votre boîte de réception.',
  closeButton: 'Fermer',
  introText: 'Nous vous enverrons un bon pour votre prochain séjour. Veuillez entrer votre adresse e-mail.',
  privacyNote: 'Objectif : vous envoyer des informations de réservation. En soumettant, vous acceptez notre politique de confidentialité.',
  labelName: 'Nom (optionnel)',
  labelEmail: 'Adresse e-mail',
  placeholderName: 'Jean Dupont',
  placeholderEmail: 'example@email.com',
  cancelButton: 'Annuler',
  submitButton: 'Obtenir le bon',
  submittingButton: 'Envoi en cours...',
  errorSendFailed: 'Échec de l\'envoi. Veuillez réessayer plus tard.'
}

/** Español */
const COPY_ES: CouponCopy = {
  couponButton: 'Cupón de descuento',
  modalTitle: 'Obtener un cupón',
  successTitle: 'Cupón enviado.',
  successDescription: 'Hemos enviado el cupón a su correo electrónico. Por favor, revise su bandeja de entrada.',
  closeButton: 'Cerrar',
  introText: 'Le enviaremos un cupón para su próxima estancia. Por favor, introduzca su correo electrónico.',
  privacyNote: 'Finalidad: enviarle información de reservas. Al enviar, acepta nuestra política de privacidad.',
  labelName: 'Nombre (opcional)',
  labelEmail: 'Correo electrónico',
  placeholderName: 'Juan García',
  placeholderEmail: 'example@email.com',
  cancelButton: 'Cancelar',
  submitButton: 'Obtener cupón',
  submittingButton: 'Enviando...',
  errorSendFailed: 'Error al enviar. Por favor, inténtelo de nuevo más tarde.'
}

/** Deutsch */
const COPY_DE: CouponCopy = {
  couponButton: 'Gutschein',
  modalTitle: 'Gutschein erhalten',
  successTitle: 'Gutschein gesendet.',
  successDescription: 'Wir haben den Gutschein an Ihre E-Mail-Adresse gesendet. Bitte überprüfen Sie Ihren Posteingang.',
  closeButton: 'Schließen',
  introText: 'Wir senden Ihnen einen Gutschein für Ihren nächsten Aufenthalt. Bitte geben Sie Ihre E-Mail-Adresse ein.',
  privacyNote: 'Zweck: Zusendung von Buchungsinformationen. Mit dem Absenden stimmen Sie unserer Datenschutzrichtlinie zu.',
  labelName: 'Name (optional)',
  labelEmail: 'E-Mail-Adresse',
  placeholderName: 'Max Mustermann',
  placeholderEmail: 'example@email.com',
  cancelButton: 'Abbrechen',
  submitButton: 'Gutschein erhalten',
  submittingButton: 'Wird gesendet...',
  errorSendFailed: 'Senden fehlgeschlagen. Bitte versuchen Sie es später erneut.'
}

/** 한국어 */
const COPY_KO: CouponCopy = {
  couponButton: '할인 쿠폰',
  modalTitle: '쿠폰 받기',
  successTitle: '쿠폰을 발송했습니다.',
  successDescription: '등록하신 이메일 주소로 쿠폰을 보냈습니다. 확인해 주세요.',
  closeButton: '닫기',
  introText: '다음 예약 시 사용하실 수 있는 쿠폰을 보내 드립니다. 이메일 주소를 입력해 주세요.',
  privacyNote: '이용 목적: 예약 안내를 위해 사용됩니다. 전송하시면 개인정보 처리방침에 동의한 것으로 간주됩니다.',
  labelName: '이름 (선택)',
  labelEmail: '이메일 주소',
  placeholderName: '홍길동',
  placeholderEmail: 'example@email.com',
  cancelButton: '취소',
  submitButton: '쿠폰 받기',
  submittingButton: '전송 중...',
  errorSendFailed: '전송에 실패했습니다. 잠시 후 다시 시도해 주세요.'
}

/** ไทย */
const COPY_TH: CouponCopy = {
  couponButton: 'คูปองส่วนลด',
  modalTitle: 'รับคูปองส่วนลด',
  successTitle: 'ส่งคูปองแล้ว',
  successDescription: 'เราได้ส่งคูปองไปยังอีเมลของคุณแล้ว กรุณาตรวจสอบกล่องจดหมาย',
  closeButton: 'ปิด',
  introText: 'เราจะส่งคูปองสำหรับการเข้าพักครั้งถัดไปของคุณ กรุณากรอกอีเมล',
  privacyNote: 'วัตถุประสงค์: เพื่อส่งข้อมูลการจอง การส่งหมายความว่าคุณยอมรับนโยบายความเป็นส่วนตัว',
  labelName: 'ชื่อ (ไม่บังคับ)',
  labelEmail: 'อีเมล',
  placeholderName: 'สมชาย ใจดี',
  placeholderEmail: 'example@email.com',
  cancelButton: 'ยกเลิก',
  submitButton: 'รับคูปอง',
  submittingButton: 'กำลังส่ง...',
  errorSendFailed: 'ส่งไม่สำเร็จ กรุณาลองใหม่อีกครั้ง'
}

/** Tiếng Việt */
const COPY_VI: CouponCopy = {
  couponButton: 'Mã giảm giá',
  modalTitle: 'Nhận mã giảm giá',
  successTitle: 'Đã gửi mã.',
  successDescription: 'Chúng tôi đã gửi mã đến địa chỉ email của bạn. Vui lòng kiểm tra hộp thư.',
  closeButton: 'Đóng',
  introText: 'Chúng tôi sẽ gửi mã giảm giá cho lần lưu trú tiếp theo. Vui lòng nhập địa chỉ email.',
  privacyNote: 'Mục đích: Gửi thông tin đặt phòng. Khi gửi, bạn đồng ý với chính sách bảo mật của chúng tôi.',
  labelName: 'Tên (tùy chọn)',
  labelEmail: 'Địa chỉ email',
  placeholderName: 'Nguyễn Văn A',
  placeholderEmail: 'example@email.com',
  cancelButton: 'Hủy',
  submitButton: 'Nhận mã',
  submittingButton: 'Đang gửi...',
  errorSendFailed: 'Gửi thất bại. Vui lòng thử lại sau.'
}

const COPY_MAP: Record<string, CouponCopy> = {
  ja: COPY_JA,
  en: COPY_EN,
  'zh-TW': COPY_ZH_TW,
  fr: COPY_FR,
  es: COPY_ES,
  de: COPY_DE,
  ko: COPY_KO,
  th: COPY_TH,
  vi: COPY_VI
}

const FALLBACK_LANG = 'en'

/**
 * 指定言語のクーポン関連文言を返す。未対応言語の場合は en にフォールバックする。
 */
export function getCouponCopy(lang: string): CouponCopy {
  const normalized = (lang || '').trim() || FALLBACK_LANG
  return COPY_MAP[normalized] ?? COPY_MAP[FALLBACK_LANG]
}
