INSERT INTO category (
  cd, nm, img, created_dt, created_by, 
  updated_dt, updated_by, is_delete, 
  is_inactive, deleted_dt, deleted_by
) 
VALUES 
  (
    'category1', 'Tofu & Tempeh', 'Angsio_Tofu.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  ), 
  (
    'category2', 'Chicken', 'Chicken_Katsu_Curry.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  ), 
  (
    'category3', 'Seafood', 'Sup_Tom_Yum.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  ), 
  (
    'category4', 'Noodles', 'Mie_Goreng.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  ), 
  (
    'category5', 'Rice Dishes', 'Nasi_Goreng_Kampung.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  ), 
  (
    'category6', 'Desserts', 'Pisang_Goreng_Cokelat_Keju.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  ), 
  (
    'category7', 'Beverages', 'Coffee_Latte.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  ), 
  (
    'category8', 'Snacks', 'Enoki_Tempura.png', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', NULL, NULL
  );
INSERT INTO menu (
  cd, nm, img, "desc", price, category_cd, 
  created_dt, created_by, updated_dt, 
  updated_by, is_delete, is_inactive, 
  is_drink
) 
VALUES 
  (
    'menu_1', 'Angsio Tofu', 'Angsio_Tofu.png', 
    'Tofu cooked with various spices', 
    800, 'category1', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_2', 'Chicken Katsu Curry', 
    'Chicken_Katsu_Curry.png', 'Crispy chicken katsu with curry sauce', 
    1200, 'category2', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_3', 'Sup Tom Yum', 'Sup_Tom_Yum.png', 
    'Thai hot and sour soup', 900, 'category3', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'N'
  ), 
  (
    'menu_4', 'Mie Goreng', 'Mie_Goreng.png', 
    'Indonesian stir-fried noodles', 
    700, 'category4', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_5', 'Nasi Goreng Kampung', 
    'Nasi_Goreng_Kampung.png', 'Traditional Indonesian fried rice', 
    750, 'category5', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_6', 'Pisang Goreng Cokelat Keju', 
    'Pisang_Goreng_Cokelat_Keju.png', 
    'Fried banana with chocolate and cheese', 
    500, 'category6', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_7', 'Coffee Latte', 'Coffee_Latte.png', 
    'Classic coffee latte', 300, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_8', 'Enoki Tempura', 'Enoki_Tempura.png', 
    'Deep-fried enoki mushrooms', 400, 
    'category8', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_9', 'Bintang', 'Bintang.png', 
    'Popular Indonesian beer', 200, 
    'category7', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'Y'
  ), 
  (
    'menu_10', 'Blue Ocean', 'Blue_Ocean.png', 
    'Refreshing blue cocktail', 350, 
    'category7', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'Y'
  ), 
  (
    'menu_11', 'Caramel Latte', 'Caramel_Latte.png', 
    'Sweet caramel-flavored latte', 
    300, 'category7', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'Y'
  ), 
  (
    'menu_12', 'Chicken Skin Original', 
    'Chicken_Skin_Original.png', 'Crispy fried chicken skin', 
    250, 'category2', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_13', 'Chicken Wing Cabe Garam', 
    'Chicken_Wing_Cabe_Garam.png', 
    'Spicy chicken wings', 400, 'category2', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'N'
  ), 
  (
    'menu_14', 'Guiness', 'Guiness.jpg', 
    'Classic Irish stout', 350, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_15', 'Heineken', 'Heineken.jpg', 
    'Popular Dutch beer', 300, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_16', 'Ice Mojito Rainbow', 
    'Ice_Mojito_Rainbow.png', 'Colorful mojito', 
    400, 'category7', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'Y'
  ), 
  (
    'menu_17', 'Juice Alpukat', 'Juice_Alpukat.png', 
    'Avocado juice', 250, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_18', 'Juice Mangga', 'Juice_Mangga.png', 
    'Mango juice', 250, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_19', 'Juice Melon', 'Juice_Melon.png', 
    'Melon juice', 250, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_20', 'Juice Naga', 'Juice_Naga.png', 
    'Dragon fruit juice', 250, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_21', 'Juice Nanas', 'Juice_Nanas.png', 
    'Pineapple juice', 250, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_22', 'Jus Strawberry', 'Jus_Strawberry.png', 
    'Strawberry juice', 250, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  ), 
  (
    'menu_23', 'Mie Jawa Indonesia', 
    'Mie_Jawa_Indonesia.png', 'Indonesian style Javanese noodles', 
    800, 'category4', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_24', 'Mie Laksa Singapura', 
    'Mie_Laksa_Singapura.png', 'Singaporean style laksa noodles', 
    850, 'category4', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_25', 'Nasi Iga Balado', 'Nasi_Iga_Balado.png', 
    'Spicy beef ribs with rice', 1000, 
    'category5', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_26', 'Sapi Lada Hitam', 'Sapi_Lada_Hitam.png', 
    'Beef in black pepper sauce', 1100, 
    'category6', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_27', 'Sosis And Chips', 'Sosis_And_Chips.png', 
    'Sausages with chips', 600, 'category6', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'N'
  ), 
  (
    'menu_28', 'Spaghetti Aglio Olio', 
    'Spaghetti_Aglio_Olio.png', 'Italian pasta with garlic and olive oil', 
    700, 'category6', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_29', 'Tahu Cabe Garam', 'Tahu_Cabe_Garam.png', 
    'Spicy tofu', 400, 'category1', '2024-05-30 12:00:00', 
    'Admin', '2024-05-30 12:00:00', 
    'Admin', 'N', 'N', 'N'
  ), 
  (
    'menu_30', 'V60 Coffee', 'V60_Coffee.png', 
    'Pour-over coffee', 350, 'category7', 
    '2024-05-30 12:00:00', 'Admin', 
    '2024-05-30 12:00:00', 'Admin', 
    'N', 'N', 'Y'
  );
INSERT INTO public."table" (
  cd, nm, "desc", is_billiard, created_dt, 
  created_by, updated_dt, updated_by, 
  is_inactive, is_delete
) 
VALUES 
  (
    '10', '10', '10', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '11', '11', '11', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '12', '12', '12', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '13', '13', '13', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '14', '14', '14', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '15', '15', '15', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '16', '16', '16', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '17', '17', '17', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '18', '18', '18', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '19', '19', '19', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  );
INSERT INTO public."table" (
  cd, nm, "desc", is_billiard, created_dt, 
  created_by, updated_dt, updated_by, 
  is_inactive, is_delete
) 
VALUES 
  (
    '20', '20', '20', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '21', '21', '21', 'N', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '1', '1', '1', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '2', '2', '2', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '3', '3', '3', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '4', '4', '4', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '5', '5', '5', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '6', '6', '6', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '7', '7', '7', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  ), 
  (
    '8', '8', '8', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  );
INSERT INTO public."table" (
  cd, nm, "desc", is_billiard, created_dt, 
  created_by, updated_dt, updated_by, 
  is_inactive, is_delete
) 
VALUES 
  (
    '9', '9', '9', 'Y', NULL, NULL, NULL, 
    NULL, 'N', 'N'
  );
INSERT INTO public."role" (
  cd, nm, created_by, created_dt, updated_by, 
  updated_dt, is_delete
) 
VALUES 
  (
    'owner', 'owner', 'owner', NULL, NULL, 
    NULL, 'N'
  ), 
  (
    'supervisor', 'supervisor', 'owner', 
    NULL, NULL, NULL, 'N'
  ), 
  (
    'kasir', 'kasir', 'owner', NULL, NULL, 
    NULL, 'N'
  ), 
  (
    'barista', 'barista', 'owner', NULL, 
    NULL, NULL, 'N'
  ), 
  (
    'kitchen', 'kitchen', 'owner', NULL, 
    NULL, NULL, 'N'
  ), 
  (
    'waiter', 'waiter', 'owner', NULL, 
    NULL, NULL, 'N'
  );
INSERT INTO public."user" (
  cd, name, username, role_cd, created_by, 
  created_dt, updated_by, updated_dt, 
  is_inactive, is_delete, is_resign, 
  img
) 
VALUES 
  (
    'owner', 'owner', 'owner', 'owner', 
    NULL, NULL, NULL, NULL, 'N', 'N', 'N', 
    NULL
  ), 
  (
    'e247cffd398c4e7d88b9578b422cd371', 
    'nigun', 'nigun', 'supervisor', 'admin', 
    '2024-07-05 04:22:07.589845', NULL, 
    NULL, 'N', 'N', 'N', NULL
  ), 
  (
    '9ff9e44a509d4c91a6a54778150b02ce', 
    'barista', 'barista', 'barista', 
    'admin', '2024-07-05 05:35:57.797896', 
    NULL, NULL, 'N', 'N', 'N', NULL
  ), 
  (
    'a31c3da69d64490f82533ee6887acb50', 
    'kitchen', 'kitchen', 'kitchen', 
    'admin', '2024-07-05 05:36:11.257438', 
    NULL, NULL, 'N', 'N', 'N', NULL
  ), 
  (
    'a0f5067529124c4c81b3010127caf98b', 
    'kasir', 'kasir', 'kasir', 'admin', 
    '2024-07-05 05:36:21.14184', NULL, 
    NULL, 'N', 'N', 'N', NULL
  ), 
  (
    '7a96e5ac8079439aa63ca1f083f93ccd', 
    'waiter', 'waiter', 'waiter', 'admin', 
    '2024-07-05 08:51:48.801641', NULL, 
    NULL, 'N', 'N', 'N', NULL
  );
INSERT INTO public.user_credential (
  cd, user_cd, "password", created_dt, 
  updated_dt, is_delete
) 
VALUES 
  (
    'fa778289911a4e01ab4b4a9c8ec4a7b7', 
    'e247cffd398c4e7d88b9578b422cd371', 
    '$2b$12$WkPBYpviivy5vLASM2ey7ekIJ8UNO4ZJuu.dcnCch93XQ/YWjUra2', 
    '2024-07-05 04:22:08.170968', NULL, 
    'N'
  ), 
  (
    '11b9be40-c20c-4ac1-8412-02892748326e', 
    'owner', '$2b$12$WkPBYpviivy5vLASM2ey7ekIJ8UNO4ZJuu.dcnCch93XQ/YWjUra2', 
    NULL, NULL, 'N'
  ), 
  (
    'fa640a63e1c2432aab9230f694bcaea5', 
    '9ff9e44a509d4c91a6a54778150b02ce', 
    '$2b$12$CFg3HJ40QStCVhuMN7Fxquym8VLoY1AKfiGLESab1Yi92C.G0YXWG', 
    '2024-07-05 05:35:58.353413', NULL, 
    'N'
  ), 
  (
    '2a3f2d52da1e433dbb59d03bc1164b18', 
    'a31c3da69d64490f82533ee6887acb50', 
    '$2b$12$E74U0/3tM8ryrZ03tGlym.YEM3obBHkUYPYmP/4dyr2fqaSPyFVNu', 
    '2024-07-05 05:36:11.834474', NULL, 
    'N'
  ), 
  (
    '138d581ed27b435d98ea5261984f0021', 
    'a0f5067529124c4c81b3010127caf98b', 
    '$2b$12$0JDxrMzjcyfLQQmEMsNZ9uHcU/B.d0Mnrk8Ypo8kzdlR.cHsFI6BO', 
    '2024-07-05 05:36:21.696307', NULL, 
    'N'
  ), 
  (
    '65dab2878d334fb789f6402a737f173f', 
    '7a96e5ac8079439aa63ca1f083f93ccd', 
    '$2b$12$7lAUUg67Aes84zgKx9XkmelbVTRmhmh8fRMM1TH7XRcFKg9GZNBQG', 
    '2024-07-05 08:51:49.369053', NULL, 
    'N'
  );
INSERT INTO public.app_setting (
  cd, nm, "desc", value, created_dt, created_by, 
  is_inactive, is_delete
) 
VALUES 
  (
    'service', 'SERVICE', NULL, '0.05', 
    NULL, NULL, 'N', 'N'
  ), 
  (
    'time_interval', 'TIME INTERVAL', 
    NULL, '30', NULL, NULL, 'N', 'N'
  ), 
  (
    'restaurant_enable', 'ENABLE RESTAURANT', 
    NULL, 'Y', NULL, NULL, 'N', 'N'
  ), 
  (
    'pb1', 'PB1', NULL, '0.15', NULL, NULL, 
    'N', 'N'
  );
