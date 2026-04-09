CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT := 1;
    bad_data TEXT := '';
BEGIN
    IF array_length(p_names, 1) != array_length(p_phones, 1) THEN
        RAISE NOTICE 'Arrays have different lengths';
        RETURN;
    END IF;

    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^[0-9+]+$' THEN
            INSERT INTO contacts(name, phone)
            VALUES (p_names[i], p_phones[i]);
        ELSE
            bad_data := bad_data || p_names[i] || ':' || p_phones[i] || ', ';
        END IF;
    END LOOP;

    RAISE NOTICE 'Invalid data: %', bad_data;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_value OR phone = p_value;
END;
$$;