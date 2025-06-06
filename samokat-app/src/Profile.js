import React, { useEffect, useState } from 'react';
import styles from './Profile.module.scss';

function Profile() {
  const [userData, setUserData] = useState(null);
  const [rentals, setRentals] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchUserData = async () => {
      const res = await fetch('http://localhost:8000/users/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setUserData(data);
    };

    fetchUserData();
  }, [token]);

  const fetchRentals = async () => {
    const res = await fetch('http://localhost:8000/rentals/history', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setRentals(data);
    setIsModalOpen(true); // Открыть модальное окно
  };

  const closeModal = () => {
    setIsModalOpen(false); // Закрыть модальное окно
  };

  if (!userData) return <p className={styles.message}>Загрузка профиля...</p>;

  return (
    <div className={styles.profileContainer}>
      <h3>Профиль</h3>
      <p><strong>Баланс:</strong> {userData.balance} руб.</p>
      <p><strong>Имя пользователя:</strong> {userData.username}</p>
      <p><strong>Номер телефона:</strong> {userData.phone}</p>
      <button className={styles.historyButton} onClick={fetchRentals}>
        История поездок
      </button>

      {/* Модальное окно */}
      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h4>История поездок</h4>
            <button className={styles.closeButton} onClick={closeModal}>
              Закрыть
            </button>
            <div className={styles.rentalsList}>
              {rentals.length > 0 ? (
                rentals.map((rental, index) => (
                  <div key={index} className={styles.rentalCard}>
                    <p><strong>Рама:</strong> {rental['Рама']}</p>
                    <p><strong>Время старта:</strong> {rental['Время старта']}</p>
                    <p><strong>Время окончания:</strong> {rental['Время окончания']}</p>
                    <p><strong>Продолжительность:</strong> {rental['Продолжительность (минуты)']} минут</p>
                    <p><strong>Сумма:</strong> {rental['Сумма (рубли)']} руб.</p>
                    <p><strong>Тариф:</strong> {rental['Тариф']}</p>
                  </div>
                ))
              ) : (
                <p>Нет записей о поездках.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;