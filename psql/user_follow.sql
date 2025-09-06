CREATE TABLE user_follow (
    follow_id SERIAL PRIMARY KEY,
    follower_uid INT NOT NULL REFERENCES userauth(uid) ON DELETE CASCADE, -- フォローする人
    followee_uid INT NOT NULL REFERENCES userauth(uid) ON DELETE CASCADE, -- フォローされる人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(follower_uid, followee_uid), -- 重複禁止
    CHECK (follower_uid <> followee_uid) -- 自分自身をフォロー禁止
);


CREATE TABLE follow_requests (
    request_id SERIAL PRIMARY KEY,
    sender_uid INT NOT NULL REFERENCES userauth(uid) ON DELETE CASCADE,  -- リクエストを送った人
    receiver_uid INT NOT NULL REFERENCES userauth(uid) ON DELETE CASCADE, -- リクエストを受け取った人
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'accepted', 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sender_uid, receiver_uid), -- 重複禁止
    CHECK (sender_uid <> receiver_uid) -- 自分自身に送信禁止
);
