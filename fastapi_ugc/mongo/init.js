function log(level, message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${level}] ${message}`);
}

try {
    conn = new Mongo();
    db = conn.getDB("ugc_movies");
    log("INFO", "Успешное подключение к базе данных 'ugc_movies'");
} catch (error) {
    log("ERROR", `Ошибка подключения к базе данных: ${error}`);
    throw error;
}

db.createCollection("user_likes");
db.createCollection("user_bookmarks");
db.createCollection("user_reviews");


try {
    db.user_likes.createIndex({ movie_id: 1, user_id: 1 }, { unique: true });
    log("INFO", "Уникальный индекс для коллекции 'user_likes' успешно создан");
} catch (error) {
    log("ERROR", `Ошибка при создании индекса для коллекции 'user_likes': ${error}`);
}

try {
    db.user_bookmarks.createIndex({ movie_id: 1, user_id: 1 }, { unique: true });
    log("INFO", "Уникальный индекс для коллекции 'user_bookmarks' успешно создан");
} catch (error) {
    log("ERROR", `Ошибка при создании индекса для коллекции 'user_bookmarks': ${error}`);
}

try {
    db.user_reviews.createIndex({ movie_id: 1, user_id: 1 }, { unique: true });
    log("INFO", "Уникальный индекс для коллекции 'user_reviews' успешно создан");
} catch (error) {
    log("ERROR", `Ошибка при создании индекса для коллекции 'user_reviews': ${error}`);
}
