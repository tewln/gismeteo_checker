Данный бот ежедневно собирает погоду c сайта gismeteo.ru и сохраняет для реализации дневника погоды (https://www.gismeteo.ru/diary/) - наблюдения в оригинальном дневнике не ведутся уже на протяжении года. В базе данных есть информация лишь о прошедших днях - данные собираются день в день, данные о будующих днях не собираются ввиду возможной неточности и неактуальности для заполнения настоящего дневника погоды школьником.

Для запуска требуется сделать файл build.sh исполняемым и запустить его.
После запуска бота, необходимо обратиться к нему в телеграм с командой '/start' - для начала работы с дневником погоды.
Для получения дневника погоды за какой-либо период, следует отправить команду '/weather', после которой через пробел указываются: дата в формате (ДД.ММ.ГГГГ), период (в днях; не более одного месяца; отсчёт начинается с единицы, где 1 - день, указанный началом периода, 31 - день, спустя 30 дней с начала периода (указываемой даты)).
Для получения списка команд следует отправить команду '/help'.

Для работы требуется установить Docker-compose, Docker и Python.
Также, в корневой папке следует создать файл .env, в котором указать переменную 'API_TOKEN' и её значение (ключ API) через знак '='.

