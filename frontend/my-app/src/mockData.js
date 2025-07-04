/**
 * Hierarchical Mock Data.
 * Structure: Region -> Goal -> Project
 * Each project contains its own indicators and measures.
 */
export const mockData = {
  "Псковская область": {
    goals: [
      {
        name: "Сохранение населения, здоровье и благополучие людей",
        projects: [
          {
            name: "Нацпроект 'Здравоохранение'",
            indicators: [
              {
                name: "Ожидаемая продолжительность жизни, лет",
                rfValue: 73.4, regionValue: 71.3, targetValue: 78.0, isReversed: false,
                budget: { allocated: 3200000000, executed: 3100000000 },
                chartData: {
                  labels: ['2021', '2022', '2023', '2024'],
                  datasets: [
                    { label: 'ОПЖ в Псковской области, лет', data: [69.8, 70.1, 70.8, 71.3] },
                    { label: 'Среднее по РФ, лет', data: [71.5, 72.1, 72.9, 73.4] },
                  ],
                },
              },
            ],
            measures: ["Модернизация первичного звена здравоохранения.", "Строительство новых ФАПов."],
          },
          {
            name: "Нацпроект 'Демография'",
            indicators: [
              {
                name: "Коэффициент рождаемости на 1000 чел.",
                rfValue: 9.1, regionValue: 8.5, targetValue: 10.5, isReversed: false,
                budget: { allocated: 950000000, executed: 800000000 },
                chartData: {
                  labels: ['2021', '2022', '2023', '2024'],
                  datasets: [
                    { label: 'Рождаемость в Псковской области', data: [8.9, 8.7, 8.6, 8.5] },
                    { label: 'Среднее по РФ', data: [9.5, 9.4, 9.2, 9.1] },
                  ],
                },
              },
            ],
            measures: ["Выплаты материнского капитала.", "Льготная ипотека для семей с детьми."],
          },
        ],
      },
      {
        name: "Возможности для самореализации и развития талантов",
        projects: [
          {
            name: "Нацпроект 'Образование'",
            indicators: [
               {
                name: "Доля детей с высокими результатами в олимпиадах, %",
                rfValue: 15, regionValue: 12, targetValue: 18, isReversed: false,
                budget: { allocated: 1200000000, executed: 1100000000 },
                chartData: {
                  labels: ['2021', '2022', '2023', '2024'],
                  datasets: [
                    { label: 'Доля олимпиадников в Псковской области, %', data: [10, 11, 11.5, 12] },
                    { label: 'Среднее по РФ, %', data: [13, 14, 14.5, 15] },
                  ],
                },
              },
            ],
            measures: ["Создание центров 'Точка роста'.", "Поддержка одаренных детей."],
          }
        ]
      }
    ],
  },
  "Ленинградская область": {
    goals: [
       {
        name: "Комфортная и безопасная среда для жизни",
        projects: [
          {
            name: "Нацпроект 'Безопасные качественные дороги'",
            indicators: [
              {
                name: "Доля дорог в нормативном состоянии, %",
                rfValue: 85.0, regionValue: 88.2, targetValue: 90.0, isReversed: false,
                budget: { allocated: 15000000000, executed: 14800000000 },
                chartData: {
                  labels: ['2021', '2022', '2023', '2024'],
                  datasets: [
                    { label: 'Дороги в нормативном состоянии в Лен. области, %', data: [79.1, 83.4, 86.0, 88.2] },
                    { label: 'Среднее по РФ, %', data: [81.0, 82.5, 84.1, 85.0] },
                  ],
                },
              },
            ],
            measures: ["Ремонт и капитальный ремонт региональных дорог.", "Внедрение интеллектуальных транспортных систем."],
          },
           {
            name: "Нацпроект 'Жилье и городская среда'",
            indicators: [
              {
                name: "Количество благоустроенных общественных территорий",
                rfValue: 500, regionValue: 550, targetValue: 600, isReversed: false,
                budget: { allocated: 5000000000, executed: 4900000000 },
                chartData: {
                  labels: ['2021', '2022', '2023', '2024'],
                  datasets: [
                    { label: 'Благоустроенные территории в Лен. области', data: [350, 420, 490, 550] },
                    { label: 'Среднее по РФ', data: [300, 380, 450, 500] },
                  ],
                },
              },
            ],
            measures: ["Программы благоустройства парков и скверов.", "Вовлечение граждан в решение вопросов развития городской среды."],
          }
        ]
      }
    ]
  }
};
