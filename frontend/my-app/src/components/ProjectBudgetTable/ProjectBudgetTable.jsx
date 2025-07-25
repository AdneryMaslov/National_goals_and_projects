import React, { useState } from 'react';
import styles from './ProjectBudgetTable.module.css';
import BudgetDetailModal from '../BudgetDetailModal/BudgetDetailModal.jsx';

const API_URL = '/api';

const formatNumber = (value) => {
  const number = parseFloat(value);
  if (isNaN(number)) return 'N/A';

  const formattedNumber = new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(number);

  return String(formattedNumber);
};

const BudgetRow = ({ item }) => {
  const allocatedNum = parseFloat(item.allocated);
  const executedNum = parseFloat(item.executed);

  const executionPercentage = !isNaN(allocatedNum) && allocatedNum > 0 && !isNaN(executedNum)
    ? (executedNum / allocatedNum * 100)
    : 0;

  return (
    <tr>
      <td>{item.name}</td>
      <td className={styles.numberCell} style={{ textAlign: 'center' }}>{formatNumber(item.allocated)}</td>
      <td className={styles.numberCell} style={{ textAlign: 'center' }}>{formatNumber(item.executed)}</td>
      <td className={`${styles.numberCell} text-bold`} style={{ textAlign: 'center' }}>{executionPercentage.toFixed(1)}%</td>
    </tr>
  );
};

const ProjectBudgetTable = ({ budget, selectedRegion, selectedProject, selectedYear }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);
  const [isLoadingModal, setIsLoadingModal] = useState(false);

  const handleOpenDetails = async () => {
    console.log("Кнопка 'Подробнее' нажата");
    console.log("Полученные данные для запроса:", { selectedProject, selectedRegion, selectedYear });

    if (!selectedProject || !selectedRegion) {
        console.error("Запрос отменен: selectedProject или selectedRegion отсутствуют.");
        return;
    }

    setIsModalOpen(true);
    setIsLoadingModal(true);

    try {
      const response = await fetch(`${API_URL}/budgets/history?project_id=${selectedProject.id}&region_id=${selectedRegion.id}&year=${selectedYear}`);

      // --- ИЗМЕНЕНИЕ ЗДЕСЬ: Добавляем проверку типа ответа ---
      const contentType = response.headers.get("content-type");
      if (!response.ok || !contentType || !contentType.includes("application/json")) {
          const responseText = await response.text();
          throw new Error(`Ошибка: Некорректный ответ от сервера. Статус: ${response.status}. Ответ: ${responseText.slice(0, 100)}...`);
      }

      const data = await response.json();
      setModalData(data);
    } catch (error) {
      console.error("Ошибка при загрузке деталей бюджета:", error);
      setModalData(null);
    } finally {
      setIsLoadingModal(false);
    }
  };

  let displayBudget;
  let hasData = budget && budget.length > 0;

  if (hasData) {
    displayBudget = budget;
  } else {
    const rows = [];
    if (selectedRegion?.name !== "Российская Федерация") {
        rows.push({ name: "Российская Федерация", allocated: null, executed: null });
    }
    rows.push({ name: selectedRegion?.name || "Выбранный регион", allocated: null, executed: null });
    displayBudget = rows;
  }

  return (
    <>
      <div className={styles.budgetTableContainer}>
        <div className={styles.header}>
            <h4>Бюджет национального проекта</h4>
            <button onClick={handleOpenDetails} className={styles.detailsButton}>
                Подробнее
            </button>
        </div>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th style={{ textAlign: 'center', fontWeight: 'bold', color: 'black' }}>Уровень</th>
                <th style={{ textAlign: 'center', fontWeight: 'bold', color: 'black' }}>Бюджет выделено, млн ₽</th>
                <th style={{ textAlign: 'center', fontWeight: 'bold', color: 'black' }}>Бюджет исполнено, млн ₽</th>
                <th style={{ textAlign: 'center', fontWeight: 'bold', color: 'black' }}>Исполнено, %</th>
              </tr>
            </thead>
            <tbody>
              {displayBudget.map(item => (
                <BudgetRow key={item.name} item={item} />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <BudgetDetailModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          data={modalData}
          isLoading={isLoadingModal}
          projectName={selectedProject?.name}
          regionName={selectedRegion?.name}
          year={selectedYear}
        />
      )}
    </>
  );
};

export default ProjectBudgetTable;
