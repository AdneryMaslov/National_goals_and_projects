/**
 * Hierarchical Mock Data with Indicators.
 * Structure: Region -> Goal -> Project -> { budget, metrics: [ { name, indicators: [...] } ] }
 */
export const mockData = {
  "Псковская область": {
    goals: [
      {
        name: "Сохранение населения, здоровье и благополучие людей",
        projects: [
          {
            name: "Нацпроект 'Здравоохранение'",
            budget: {
              allocated: 5000000000,
              executed: 4850000000,
            },
            metrics: [
              {
                name: "Снижение смертности населения",
                indicators: [
                  { name: "Смертность от болезней системы кровообращения (на 100 тыс. чел.)", regionValue: 520, rfValue: 490, targetValue: 450, isReversed: true },
                  { name: "Смертность от новообразований (на 100 тыс. чел.)", regionValue: 210, rfValue: 195, targetValue: 185, isReversed: true },
                ]
              },
              {
                name: "Обеспечение качества и доступности мед. помощи",
                indicators: [
                  { name: "Обеспеченность врачами (на 10 тыс. чел.)", regionValue: 35, rfValue: 42, targetValue: 45, isReversed: false },
                  { name: "Охват граждан проф. медосмотрами, %", regionValue: 65, rfValue: 70, targetValue: 80, isReversed: false },
                ]
              }
            ],
            measures: ["Модернизация первичного звена здравоохранения.", "Строительство новых ФАПов.", "Программы по борьбе с сердечно-сосудистыми заболеваниями."],
          },
          {
            name: "Нацпроект 'Демография'",
            budget: {
              allocated: 1200000000,
              executed: 1150000000,
            },
            metrics: [
              {
                name: "Повышение рождаемости",
                indicators: [
                   { name: "Суммарный коэффициент рождаемости", regionValue: 1.4, rfValue: 1.5, targetValue: 1.7, isReversed: false },
                ]
              }
            ],
            measures: ["Выплаты материнского капитала.", "Льготная ипотека для семей с детьми."],
          },
        ],
      },
    ],
  },
  "Ленинградская область": {
    goals: [
       {
        name: "Комфортная и безопасная среда для жизни",
        projects: [
          {
            name: "Нацпроект 'Безопасные качественные дороги'",
            budget: {
              allocated: 15000000000,
              executed: 14800000000,
            },
            metrics: [
              {
                name: "Качество дорожной сети",
                indicators: [
                  { name: "Доля дорог в нормативном состоянии, %", regionValue: 88.2, rfValue: 85.0, targetValue: 90.0, isReversed: false },
                  { name: "Доля дорог, работающих в режиме перегрузки, %", regionValue: 12, rfValue: 10, targetValue: 8, isReversed: true },
                ]
              }
            ],
            measures: ["Ремонт и капитальный ремонт региональных дорог.", "Внедрение интеллектуальных транспортных систем."],
          },
        ]
      }
    ]
  }
};
