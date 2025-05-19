// Sabit hava durumu verileri
const weatherData = {
  temperature: 19,
  condition: 'Parçalı bulutlu',
  humidity: 65,
  windSpeed: 10,
  icon: '02d'
};

export const getWeatherData = async () => {
  try {
    // Gerçek API entegrasyonu için burada API çağrısı yapılacak
    // Şimdilik sabit veriyi döndürüyoruz
    return weatherData;
  } catch (error) {
    console.error('Hava durumu verisi alınamadı:', error);
    return weatherData;
  }
}; 