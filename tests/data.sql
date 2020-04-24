INSERT INTO user (username, password)
VALUES
  (
    'test',
    'pbkdf2:sha256:150000$gMtaFovv$008c774da46301815157070e46ea57c2b8272c70d150d04fd33d8b9c1b8c7c2b' -- password is "test"
  ),
  (
    'other',
    'pbkdf2:sha256:150000$FKWCNuUj$238cf65f2aead11ce22abeb0a718e130120acb893ca3bc569645dab27ea157c3' -- password is "other"
  );
INSERT INTO post (title, body, author_id, created, is_published)
VALUES
  (
    'test draft post',
    'test' || x'0a' || 'draft body',
    1,
    '2018-01-01 00:00:00',
    0
  ),
  (
    'test published post',
    'test' || x'0a' || 'published body',
    1,
    '2017-01-01 00:00:00',
    1
  );