import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import styles from './Protected.module.scss';
import Profile from './Profile';
import MapView from './MapView';

function ProtectedPage() {
  const navigate = useNavigate();
  const [role, setRole] = useState(null);
  const [activeTab, setActiveTab] = useState('menu');

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/');
        return;
      }

      try {
        const decoded = jwtDecode(token);
        setRole(decoded.role);
      } catch (error) {
        localStorage.removeItem('token');
        navigate('/');
      }
    };

    verifyToken();
  }, [navigate]);

  if (role === null) return <p className={styles.message}>Загрузка...</p>;

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        {activeTab === 'profile' && <Profile />}
        {activeTab === 'map' && <MapView />}
        {activeTab === 'menu' && (
          <>
            {role === 1 && <AdminMenu />}
            {role === 2 && <ManagerMenu />}
            {role === 3 && <UserMenu />}
          </>
        )}
      </div>

      <div className={styles.bottomMenu}>
        <button
          className={`${styles.menuButton} ${activeTab === 'profile' ? styles.active : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Профиль
        </button>
        <button
          className={`${styles.menuButton} ${activeTab === 'map' ? styles.active : ''}`}
          onClick={() => setActiveTab('map')}
        >
          Карта
        </button>
        <button
          className={`${styles.menuButton} ${activeTab === 'menu' ? styles.active : ''}`}
          onClick={() => setActiveTab('menu')}
        >
          Меню
        </button>
      </div>
    </div>
  );
}

function AdminMenu() {
  const [showForm, setShowForm] = useState(false);
  const [scooter, setScooter] = useState({
    model: '',
    location: '',
    frame: '',
    battery: '',
    status: '',
    connection_status: ''
  });
  const [scooters, setScooters] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRentalModalOpen, setIsRentalModalOpen] = useState(false);
  const [frameInput, setFrameInput] = useState('');
  const [scooterData, setScooterData] = useState(null);
  const [currentRental, setCurrentRental] = useState(null);
  const [rentalCost, setRentalCost] = useState(0);
  const [rentalTime, setRentalTime] = useState(0);
  const token = localStorage.getItem('token');
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const getScooters = async () => {
    const res = await fetch('http://localhost:8000/scooters/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setScooters(data);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleChange = (e) => {
    setScooter({ ...scooter, [e.target.name]: e.target.value });
  };

  const fetchData = async (endpoint, method = 'GET', body = null) => {
    const res = await fetch(`http://localhost:8000${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: body ? JSON.stringify(body) : null,
    });

    const data = await res.json();

    if (endpoint === '/scooters') {
      setScooters(data);
    } else {
      alert(data.message || JSON.stringify(data));
    }
  };

  const toggleForm = () => setShowForm(!showForm);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchData('/scooter/add_scooter', 'POST', scooter);
    setShowForm(false);
  };

  // Функция аренды самоката
  const openRentalModal = () => {
    setIsRentalModalOpen(true);
    setFrameInput('');
    setScooterData(null);
  };

  const handleFrameSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:8000/scooters/by-frame/${frameInput}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      setScooterData(data);
    } catch (error) {
      alert('Ошибка при получении данных самоката');
    }
  };

  const startRental = async (tariffId) => {
    try {
      const res = await fetch('http://localhost:8000/rentals/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ frame: frameInput, tariff_id: tariffId }),
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      setCurrentRental({
        ...data,
        tariff_price: tariffId === 1 ? 5.00 : 100.00, // Цены тарифов
      });
      setIsRentalModalOpen(false);
    } catch (error) {
      alert('Ошибка при начале аренды');
    }
  };

  const endRental = async () => {
    try {
      const res = await fetch(`http://localhost:8000/rentals/${currentRental.id}/end`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      alert(`Аренда завершена! Стоимость поездки составила: ${rentalCost.toFixed(2)} руб.`);
      setCurrentRental(null);
      setRentalCost(0);
      setRentalTime(0);
    } catch (error) {
      alert('Ошибка при завершении аренды');
    }
  };

  useEffect(() => {
    if (currentRental) {
      const interval = setInterval(() => {
        setRentalTime((prev) => prev + 1);
        if (currentRental.tariff_id === 1) {
          setRentalCost(rentalTime * currentRental.tariff_price);
        } else {
          setRentalCost(currentRental.tariff_price);
        }
      }, 60000); // Обновление каждую минуту
      return () => clearInterval(interval);
    }
  }, [currentRental, rentalTime]);

  return (
    <div className={styles.menuSection}>
      <h3>Меню администратора</h3>
      <button className={styles.button} onClick={getScooters}>Просмотреть все самокаты</button>
      <button className={styles.button} onClick={openRentalModal}>Арендовать самокат</button>

      {/* Модальное окно для аренды */}
      {isRentalModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h4>Аренда самоката</h4>
            <button className={styles.closeButton} onClick={() => setIsRentalModalOpen(false)}>
              Закрыть
            </button>
            {!scooterData ? (
              <form onSubmit={handleFrameSubmit}>
                <div className={styles.formGroup}>
                  <input
                    className={styles.input}
                    value={frameInput}
                    onChange={(e) => setFrameInput(e.target.value.toUpperCase())}
                    placeholder="Введите номер рамы (например, GD029)"
                    pattern="[A-Z]{2}\d{3}"
                    required
                  />
                </div>
                <button type="submit" className={styles.button}>Подтвердить</button>
              </form>
            ) : (
              <div>
                <p><strong>Модель:</strong> {scooterData.model}</p>
                <p><strong>Заряд батареи:</strong> {scooterData.battery}%</p>
                <button className={styles.button} onClick={() => startRental(1)}>Поминутный</button>
                <button className={styles.button} onClick={() => startRental(2)}>Фиксированный</button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Окно текущей аренды */}
      {currentRental && (
        <div className={styles.rentalOverlay}>
          <div className={styles.rentalWindow}>
            <h4>Текущая аренда</h4>
            <p><strong>Самокат:</strong> {currentRental.frame}</p>
            <p><strong>Время:</strong> {Math.floor(rentalTime / 60)}:{(rentalTime % 60).toString().padStart(2, '0')}</p>
            <p><strong>Стоимость:</strong> {rentalCost.toFixed(2)} руб.</p>
            <button className={styles.button} onClick={endRental}>Завершить</button>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h4>Список самокатов</h4>
            <button className={styles.closeButton} onClick={closeModal}>
              Закрыть
            </button>
            <div className={styles.scootersList}>
              {scooters.length > 0 ? (
                scooters.map((scooter, index) => (
                  <div key={index} className={styles.scooterCard}>
                    <h4 className={styles.cardTitle}>{scooter.model}</h4>
                    <p><strong>Локация:</strong> {scooter.location}</p>
                    <p><strong>Рама:</strong> {scooter.frame}</p>
                    <p><strong>Батарея:</strong> {scooter.battery}%</p>
                    <p><strong>Статус:</strong> {scooter.status}</p>
                    <p><strong>Связь:</strong> {scooter.connection_status}</p>
                  </div>
                ))
              ) : (
                <p>Нет доступных самокатов.</p>
              )}
            </div>
          </div>
        </div>
      )}

      <ul className={styles.buttonList}>
        <li><button className={styles.button} onClick={toggleForm}>Добавить самокат вручную</button></li>
        <li><button className={styles.button} onClick={() => fetchData('/scooter/add_sample', 'POST')}>Добавить примеры самокатов</button></li>
        <li><button className={styles.button} onClick={() => fetchData('/scooters/delete_all', 'DELETE')}>Удалить все самокаты</button></li>
      </ul>

      {showForm && (
        <form onSubmit={handleSubmit} className={styles.container}>
          <h4>Форма добавления самоката</h4>
          <div className={styles.formGroup}>
            <input className={styles.input} name="model" placeholder="Модель" onChange={handleChange} required />
          </div>
          <div className={styles.formGroup}>
            <input className={styles.input} name="location" placeholder="Координаты" onChange={handleChange} required />
          </div>
          <div className={styles.formGroup}>
            <input className={styles.input} name="frame" placeholder="Рама" onChange={handleChange} required />
          </div>
          <div className={styles.formGroup}>
            <input className={styles.input} name="battery" placeholder="Батарея (%)" type="number" onChange={handleChange} required />
          </div>
          <div className={styles.formGroup}>
            <input className={styles.input} name="status" placeholder="Статус" onChange={handleChange} required />
          </div>
          <div className={styles.formGroup}>
            <input className={styles.input} name="connection_status" placeholder="Онлайн/оффлайн" onChange={handleChange} required />
          </div>
          <button type="submit" className={styles.button}>Добавить</button>
        </form>
      )}

      <button className={styles.logoutButton} onClick={handleLogout}>
        Выйти
      </button>
    </div>
  );
}

function ManagerMenu() {
  const token = localStorage.getItem('token');
  const [scooters, setScooters] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRentalModalOpen, setIsRentalModalOpen] = useState(false);
  const [frameInput, setFrameInput] = useState('');
  const [scooterData, setScooterData] = useState(null);
  const [currentRental, setCurrentRental] = useState(null);
  const [rentalCost, setRentalCost] = useState(0);
  const [rentalTime, setRentalTime] = useState(0);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const getScooters = async () => {
    const res = await fetch('http://localhost:8000/scooters/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setScooters(data);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const openRentalModal = () => {
    setIsRentalModalOpen(true);
    setFrameInput('');
    setScooterData(null);
  };

  const handleFrameSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:8000/scooters/by-frame/${frameInput}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      setScooterData(data);
    } catch (error) {
      alert('Ошибка при получении данных самоката');
    }
  };

  const startRental = async (tariffId) => {
    try {
      const res = await fetch('http://localhost:8000/rentals/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ frame: frameInput, tariff_id: tariffId }),
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      setCurrentRental({
        ...data,
        tariff_price: tariffId === 1 ? 5.00 : 100.00,
      });
      setIsRentalModalOpen(false);
    } catch (error) {
      alert('Ошибка при начале аренды');
    }
  };

  const endRental = async () => {
    try {
      const res = await fetch(`http://localhost:8000/rentals/${currentRental.id}/end`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      alert(`Аренда завершена! Стоимость поездки составила: ${rentalCost.toFixed(2)} руб.`);
      setCurrentRental(null);
      setRentalCost(0);
      setRentalTime(0);
    } catch (error) {
      alert('Ошибка при завершении аренды');
    }
  };

  useEffect(() => {
    if (currentRental) {
      const interval = setInterval(() => {
        setRentalTime((prev) => prev + 1);
        if (currentRental.tariff_id === 1) {
          setRentalCost(rentalTime * currentRental.tariff_price);
        } else {
          setRentalCost(currentRental.tariff_price);
        }
      }, 60000);
      return () => clearInterval(interval);
    }
  }, [currentRental, rentalTime]);

  return (
    <div className={styles.menuSection}>
      <h3>Меню менеджера</h3>
      <button className={styles.button} onClick={getScooters}>Просмотреть все самокаты</button>
      <button className={styles.button} onClick={openRentalModal}>Арендовать самокат</button>

      {isRentalModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h4>Аренда самоката</h4>
            <button className={styles.closeButton} onClick={() => setIsRentalModalOpen(false)}>
              Закрыть
            </button>
            {!scooterData ? (
              <form onSubmit={handleFrameSubmit}>
                <div className={styles.formGroup}>
                  <input
                    className={styles.input}
                    value={frameInput}
                    onChange={(e) => setFrameInput(e.target.value.toUpperCase())}
                    placeholder="Введите номер рамы (например, GD029)"
                    pattern="[A-Z]{2}\d{3}"
                    required
                  />
                </div>
                <button type="submit" className={styles.button}>Подтвердить</button>
              </form>
            ) : (
              <div>
                <p><strong>Модель:</strong> {scooterData.model}</p>
                <p><strong>Заряд батареи:</strong> {scooterData.battery}%</p>
                <button className={styles.button} onClick={() => startRental(1)}>Поминутный</button>
                <button className={styles.button} onClick={() => startRental(2)}>Фиксированный</button>
              </div>
            )}
          </div>
        </div>
      )}

      {currentRental && (
        <div className={styles.rentalOverlay}>
          <div className={styles.rentalWindow}>
            <h4>Текущая аренда</h4>
            <p><strong>Самокат:</strong> {currentRental.frame}</p>
            <p><strong>Время:</strong> {Math.floor(rentalTime / 60)}:{(rentalTime % 60).toString().padStart(2, '0')}</p>
            <p><strong>Стоимость:</strong> {rentalCost.toFixed(2)} руб.</p>
            <button className={styles.button} onClick={endRental}>Завершить</button>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h4>Список самокатов</h4>
            <button className={styles.closeButton} onClick={closeModal}>
              Закрыть
            </button>
            <div className={styles.scootersList}>
              {scooters.length > 0 ? (
                scooters.map((scooter, index) => (
                  <div key={index} className={styles.scooterCard}>
                    <h4 className={styles.cardTitle}>{scooter.model}</h4>
                    <p><strong>Локация:</strong> {scooter.location}</p>
                    <p><strong>Рама:</strong> {scooter.frame}</p>
                    <p><strong>Батарея:</strong> {scooter.battery}%</p>
                    <p><strong>Статус:</strong> {scooter.status}</p>
                    <p><strong>Связь:</strong> {scooter.connection_status}</p>
                  </div>
                ))
              ) : (
                <p>Нет доступных самокатов.</p>
              )}
            </div>
          </div>
        </div>
      )}

      <button className={styles.logoutButton} onClick={handleLogout}>
        Выйти
      </button>
    </div>
  );
}

function UserMenu() {
  const token = localStorage.getItem('token');
  const navigate = useNavigate();
  const [isRentalModalOpen, setIsRentalModalOpen] = useState(false);
  const [frameInput, setFrameInput] = useState('');
  const [scooterData, setScooterData] = useState(null);
  const [currentRental, setCurrentRental] = useState(null);
  const [rentalCost, setRentalCost] = useState(0);
  const [rentalTime, setRentalTime] = useState(0);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const fetchUserData = async () => {
    const res = await fetch('http://localhost:8000/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    alert(JSON.stringify(data));
  };

  const openRentalModal = () => {
    setIsRentalModalOpen(true);
    setFrameInput('');
    setScooterData(null);
  };

  const handleFrameSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:8000/scooters/by-frame/${frameInput}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      setScooterData(data);
    } catch (error) {
      alert('Ошибка при получении данных самоката');
    }
  };

  const startRental = async (tariffId) => {
    try {
      const res = await fetch('http://localhost:8000/rentals/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ frame: frameInput, tariff_id: tariffId }),
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      setCurrentRental({
        ...data,
        frame: frameInput,
        tariff_price: tariffId === 1 ? 5.00 : 100.00,
      });
      setIsRentalModalOpen(false);
    } catch (error) {
      alert('Ошибка при начале аренды');
    }
  };

  const endRental = async () => {
    try {
      const res = await fetch(`http://localhost:8000/rentals/${currentRental.id}/end`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail);
        return;
      }
      const data = await res.json();
      alert(`Аренда завершена! Стоимость поездки составила: ${rentalCost.toFixed(2)} руб.`);
      setCurrentRental(null);
      setRentalCost(0);
      setRentalTime(0);
    } catch (error) {
      alert('Ошибка при завершении аренды');
    }
  };

  useEffect(() => {
    if (currentRental) {
      const interval = setInterval(() => {
        setRentalTime((prev) => prev + 1);
        if (currentRental.tariff_id === 1) {
          setRentalCost((prevTime) => (prevTime + 1) * currentRental.tariff_price);
        } else {
          setRentalCost(currentRental.tariff_price);
        }
      }, 60000); // Обновление каждую минуту
      return () => clearInterval(interval);
    }
  }, [currentRental, rentalTime]);

  return (
    <div className={styles.menuSection}>
      <h3>Меню пользователя</h3>
      <button className={styles.button} onClick={fetchUserData}>Мои данные</button>
      <button className={styles.button} onClick={openRentalModal}>Арендовать самокат</button>

      {isRentalModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h4>Аренда самоката</h4>
            <button className={styles.closeButton} onClick={() => setIsRentalModalOpen(false)}>
              Закрыть
            </button>
            {!scooterData ? (
              <form onSubmit={handleFrameSubmit}>
                <div className={styles.formGroup}>
                  <input
                    className={styles.input}
                    value={frameInput}
                    onChange={(e) => setFrameInput(e.target.value.toUpperCase())}
                    placeholder="Введите номер рамы (например, GD029)"
                    pattern="[A-Z]{2}\d{3}"
                    required
                  />
                </div>
                <button type="submit" className={styles.button}>Подтвердить</button>
              </form>
            ) : (
              <div>
                <p><strong>Модель:</strong> {scooterData.model}</p>
                <p><strong>Заряд батареи:</strong> {scooterData.battery}%</p>
                <button className={styles.button} onClick={() => startRental(1)}>Поминутный</button>
                <button className={styles.button} onClick={() => startRental(2)}>Фиксированный</button>
              </div>
            )}
          </div>
        </div>
      )}

      {currentRental && (
        <div className={styles.rentalOverlay}>
          <div className={styles.rentalWindow}>
            <h4>Текущая аренда</h4>
            <p><strong>Самокат:</strong> {currentRental.frame}</p>
            <p><strong>Время:</strong> {Math.floor(rentalTime / 60)}:{(rentalTime % 60).toString().padStart(2, '0')}</p>
            <p><strong>Стоимость:</strong> {rentalCost.toFixed(2)} руб.</p>
            <button className={styles.button} onClick={endRental}>Завершить</button>
          </div>
        </div>
      )}

      <button className={styles.logoutButton} onClick={handleLogout}>
        Выйти
      </button>
    </div>
  );
}

export default ProtectedPage;