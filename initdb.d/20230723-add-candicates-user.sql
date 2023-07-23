-- ユーザーテーブルの作成
create table dora_persons(
    id int PRIMARY KEY AUTO_INCREMENT,
    user_name varchar(255),
    dora_message text not null,
    avatar_url text not null,
    created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_name)
) DEFAULT CHARSET = utf8mb4 ENGINE = InnoDB;