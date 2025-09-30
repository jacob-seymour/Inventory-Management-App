CREATE TABLE shelf (
    shelf_id VARCHAR(5) PRIMARY KEY
);

CREATE TABLE product(
	product_id INT PRIMARY KEY,
	product_name VARCHAR(100) NOT NULL,
	product_description TEXT,
	model_number VARCHAR(100) NOT NULL
);

CREATE TABLE pallet (
	pallet_id VARCHAR(4) PRIMARY KEY,
	shelf_id VARCHAR (5) NOT NULL,
	product_id INT NOT NULL,
	notes TEXT,
	FOREIGN KEY (shelf_id) REFERENCES shelf(shelf_id),
	FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE item (
	item_id INT PRIMARY KEY,
	serial_number VARCHAR (50) UNIQUE NOT NULL,
	pallet_id VARCHAR(4) NOT NULL,
	product_id INT NOT NULL,
	FOREIGN KEY (pallet_id) REFERENCES pallet(pallet_id),
	FOREIGN KEY (product_id) REFERENCES product(product_id)
);