function log(level, message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${level}] ${message}`);
}

try {
    conn = new Mongo();
    db = conn.getDB("notifications_service");
    log("INFO", "Успешное подключение к базе данных 'notifications_service'");
} catch (error) {
    log("ERROR", `Ошибка подключения к базе данных: ${error}`);
    throw error;
}


db.createCollection("movie_view_stats");
db.createCollection("users");
db.createCollection("notification_record");

try {
    db.movie_view_stats.createIndex({ title: 1 }, { unique: true });
    log("INFO", "Уникальный индекс для коллекции 'movie_view_stats' успешно создан");
} catch (error) {
    log("ERROR", `Ошибка при создании индекса для коллекции 'movie_view_stats': ${error}`);
}

try {
    db.users.createIndex({ user_id: 1 }, { unique: true });
    log("INFO", "Уникальный индекс для коллекции 'users' успешно создан");
} catch (error) {
    log("ERROR", `Ошибка при создании индекса для коллекции 'users': ${error}`);
}

try {
    db.notification_record.createIndex({ id: 1 }, { unique: true });
    log("INFO", "Уникальный индекс для коллекции 'notification_record' успешно создан");
} catch (error) {
    log("ERROR", `Ошибка при создании индекса для коллекции 'notification_record': ${error}`);
}
