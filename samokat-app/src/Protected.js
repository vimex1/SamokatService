import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import styles from './Protected.module.scss';

function ProtectedPage() {
  const navigate = useNavigate();
  const [role, setRole] = useState(null);

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/');
        return;
      }

      try {
        const response = await fetch(`http://localhost:8000/verify-token/${token}`);
        if (!response.ok) throw new Error('Token verification failed');
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
      <h2 className={styles.heading}>Добро пожаловать!</h2>
      {role === 1 && <AdminMenu />}
      {role === 2 && <ManagerMenu />}
      {role === 3 && <UserMenu />}
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
    const token = localStorage.getItem('token');
  
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
  
    return (
      <div className={styles.menuSection}>
        <h3>Меню администратора</h3>
        <ul className={styles.buttonList}>
          <li><button className={styles.button} onClick={() => fetchData('/scooters')}>Просмотр всех самокатов</button></li>
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
  
        {scooters.length > 0 && (
          <div className={styles.cardGrid}>
            {scooters.map((s, index) => (
              <div key={index} className={styles.card}>
                <h4 className={styles.cardTitle}>{s.model}</h4>
                <p><strong>Локация:</strong> {s.location}</p>
                <p><strong>Рама:</strong> {s.frame}</p>
                <p><strong>Батарея:</strong> {s.battery}%</p>
                <p><strong>Статус:</strong> {s.status}</p>
                <p><strong>Связь:</strong> {s.connection_status}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

function ManagerMenu() {
    const token = localStorage.getItem('token');
    const [scooters, setScooters] = useState([]);
  
    const getScooters = async () => {
      const res = await fetch('http://localhost:8000/scooters/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setScooters(data);
    };
  
    return (
      <div className={styles.menuSection}>
        <h3>Меню менеджера</h3>
        <button className={styles.button} onClick={getScooters}>Просмотреть все самокаты</button>
  
        {scooters.length > 0 && (
          <div className={styles.cardGrid}>
            {scooters.map((scooter, index) => (
              <div key={index} className={styles.card}>
                <h4 className={styles.cardTitle}>{scooter.model}</h4>
                <p><strong>Локация:</strong> {scooter.location}</p>
                <p><strong>Рама:</strong> {scooter.frame}</p>
                <p><strong>Батарея:</strong> {scooter.battery}%</p>
                <p><strong>Статус:</strong> {scooter.status}</p>
                <p><strong>Связь:</strong> {scooter.connection_status}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

function UserMenu() {
  const token = localStorage.getItem('token');

  const fetchUserData = async () => {
    const res = await fetch('http://localhost:8000/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    alert(JSON.stringify(data));
  };

  return (
    <div className={styles.menuSection}>
      <h3>Меню пользователя</h3>
      <button className={styles.button} onClick={fetchUserData}>Мои данные</button>
    </div>
  );
}

export default ProtectedPage;
