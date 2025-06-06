import React, { useEffect } from 'react';
import styles from './MapView.module.scss';

function MapView() {
  useEffect(() => {
    const scriptId = 'yandex-maps-script';
    if (!document.getElementById(scriptId)) {
      const script = document.createElement('script');
      script.id = scriptId;
      script.src = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU';
      script.onload = () => {
        window.ymaps.ready(() => {
          const map = new window.ymaps.Map('map', {
            center: [55.751574, 37.573856], // Координаты центра карты (Москва)
            zoom: 10,
          });

          // Добавление текущего местоположения
          navigator.geolocation.getCurrentPosition((position) => {
            const { latitude, longitude } = position.coords;
            const userLocation = new window.ymaps.Placemark([latitude, longitude], {
              balloonContent: 'Вы здесь',
            });
            map.geoObjects.add(userLocation);
            map.setCenter([latitude, longitude], 14);
          });
        });
      };
      document.body.appendChild(script);
    }
  }, []);

  return <div id="map" className={styles.map}></div>;
}

export default MapView;