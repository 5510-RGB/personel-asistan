// Yerel takvim verileri
const localEvents = [
  {
    id: 1,
    title: 'Proje Toplantısı',
    startTime: new Date(new Date().setHours(10, 0, 0, 0)),
    endTime: new Date(new Date().setHours(11, 0, 0, 0)),
    location: 'Toplantı Odası A',
    description: 'Haftalık proje değerlendirme toplantısı'
  },
  {
    id: 2,
    title: 'Öğle Yemeği',
    startTime: new Date(new Date().setHours(12, 30, 0, 0)),
    endTime: new Date(new Date().setHours(13, 30, 0, 0)),
    location: 'Yemekhane',
    description: 'Ekip öğle yemeği'
  },
  {
    id: 3,
    title: 'Müşteri Görüşmesi',
    startTime: new Date(new Date().setHours(14, 0, 0, 0)),
    endTime: new Date(new Date().setHours(15, 0, 0, 0)),
    location: 'Görüşme Odası',
    description: 'Yeni proje teklifi görüşmesi'
  }
];

export const getCalendarEvents = async () => {
  try {
    // Şu anki tarihi al
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    // Bugünün etkinliklerini filtrele
    const todayEvents = localEvents.filter(event => {
      const eventDate = new Date(event.startTime);
      return eventDate >= today && eventDate < tomorrow;
    });

    return todayEvents;
  } catch (error) {
    console.error('Takvim verisi alınamadı:', error);
    return [];
  }
}; 