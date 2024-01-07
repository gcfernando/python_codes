CREATE TABLE Contact
(
id			BIGINT NOT NULL IDENTITY(1,1),
fname		VARCHAR(100) NOT NULL,
lname		VARCHAR(100) NOT NULL,
mnumber		VARCHAR(20) NOT NULL,
maddress	VARCHAR(100) NOT NULL,
)

GO

ALTER TABLE Contact
ADD CONSTRAINT PK_Contact PRIMARY KEY (id);

GO

ALTER TABLE dbo.Contact
ADD CONSTRAINT unique_mobile UNIQUE (mnumber);

GO

ALTER TABLE dbo.Contact
ADD CONSTRAINT mail_address UNIQUE (maddress);

CREATE UNIQUE INDEX unique_mobile_index ON dbo.Contact (mnumber);

GO

CREATE UNIQUE INDEX unique_mobile_address ON dbo.Contact (maddress);

GO

CREATE OR ALTER PROC SaveContact
(
    @id BIGINT,
    @fname VARCHAR(100),
    @lname VARCHAR(100),
    @mnumber VARCHAR(20),
    @maddress VARCHAR(100)
)
AS
BEGIN
    SET NOCOUNT ON;

    -- Check for duplicate data
    IF EXISTS (SELECT * FROM dbo.Contact WHERE (mnumber = @mnumber OR maddress = @maddress) AND id != @id)
    BEGIN
        RAISERROR('Duplicate data is not allowed', 16, 10);
        RETURN;
    END

    IF @id = 0
    BEGIN
        -- Insert new contact
        INSERT INTO dbo.Contact(fname, lname, mnumber, maddress)
        VALUES (@fname, @lname, @mnumber, @maddress);
    END
    ELSE
    BEGIN
        -- Update existing contact
        UPDATE dbo.Contact
        SET fname = @fname,
            lname = @lname,
            mnumber = @mnumber,
            maddress = @maddress
        WHERE id = @id;
    END
END;

GO

CREATE OR ALTER PROC DeleteContact
(
    @id BIGINT
)
AS
BEGIN
    SET NOCOUNT ON;

	IF @id > 0
	BEGIN
		DELETE FROM dbo.Contact
		WHERE id = @id
	END
END;

GO

CREATE OR ALTER PROC SearchContact
(
    @mnumber VARCHAR(20),
    @maddress VARCHAR(100)
)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT * FROM dbo.Contact
    WHERE (ISNULL(@mnumber, '') = '' OR mnumber = @mnumber) AND
          (ISNULL(@maddress, '') = '' OR maddress = @maddress)
END;