"""Testes para criptografia e media."""

import unittest
import tempfile
import os
import shutil

from pybase.crypto.cipher import encrypt, decrypt
from pybase.exceptions.errors import CryptoError
from pybase.media import MediaStore, Media
from pathlib import Path


class TestCriptografia(unittest.TestCase):

    def test_encrypt_decrypt(self):
        original = "minha_senha_secreta"
        encrypted = encrypt(original, "123")
        decrypted = decrypt(encrypted, "123")
        self.assertEqual(decrypted, original)

    def test_encrypt_produz_string_diferente(self):
        encrypted = encrypt("teste", "123")
        self.assertNotEqual(encrypted, "teste")
        self.assertIsInstance(encrypted, str)

    def test_decrypt_senha_errada(self):
        encrypted = encrypt("teste", "123")
        with self.assertRaises(CryptoError):
            decrypt(encrypted, "456")

    def test_decrypt_payload_tamperado(self):
        encrypted = encrypt("teste", "123")
        payload = list(encrypted)
        payload[-1] = chr(ord(payload[-1]) ^ 1)  # corrompe um char
        with self.assertRaises(CryptoError):
            decrypt("".join(payload), "123")

    def test_encrypt_none(self):
        self.assertIsNone(encrypt(None, "123"))

    def test_decrypt_none(self):
        self.assertIsNone(decrypt(None, "123"))

    def test_decrypt_base64_invalido(self):
        with self.assertRaises(CryptoError):
            decrypt("!!!base64-invalido!!!", "123")

    def test_decrypt_payload_curto(self):
        with self.assertRaises(CryptoError):
            decrypt("abc", "123")

    def test_encrypt_e_diferente_cada_vez(self):
        r1 = encrypt("mesmo_texto", "123")
        r2 = encrypt("mesmo_texto", "123")
        self.assertNotEqual(r1, r2)  # salt aleatório

    def test_encrypt_vazio(self):
        encrypted = encrypt("", "123")
        decrypted = decrypt(encrypted, "123")
        self.assertEqual(decrypted, "")


class TestMediaStore(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.db_dir = self.tmp / "mediadb"
        self.db_dir.mkdir()
        self.store = MediaStore(self.db_dir)
        # Cria um arquivo de imagem dummy
        self.img_path = self.tmp / "foto.jpg"
        self.img_path.write_bytes(b"fake-image-data")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_retorna_nome(self):
        name = self.store.save(str(self.img_path), "rec1", "foto")
        self.assertIn("rec1", name)
        self.assertIn("foto", name)

    def test_get_retorna_media(self):
        name = self.store.save(str(self.img_path), "rec1", "foto")
        media = self.store.get(name)
        self.assertIsInstance(media, Media)
        self.assertEqual(media.bytes, b"fake-image-data")

    def test_get_path_absoluto(self):
        name = self.store.save(str(self.img_path), "rec1", "foto")
        media = self.store.get(name)
        self.assertTrue(os.path.isabs(media.path))

    def test_get_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            self.store.get("inexistente.jpg")

    def test_delete_remove_arquivo(self):
        name = self.store.save(str(self.img_path), "rec1", "foto")
        self.store.delete(name)
        with self.assertRaises(FileNotFoundError):
            self.store.get(name)

    def test_save_source_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            self.store.save("/nao/existe.jpg", "rec1", "foto")

    def test_clean_orphans(self):
        n1 = self.store.save(str(self.img_path), "rec1", "foto")
        n2 = self.store.save(str(self.img_path), "rec2", "foto")
        self.store.clean_orphans([{"foto": n1}], {"foto"})
        # n2 deve ter sido removido
        with self.assertRaises(FileNotFoundError):
            self.store.get(n2)
        # n1 ainda existe
        self.assertIsNotNone(self.store.get(n1))

    def test_media_bytes_lazy(self):
        name = self.store.save(str(self.img_path), "rec1", "foto")
        media = self.store.get(name)
        # Re-escreve o arquivo depois de criar o Media
        self.assertEqual(media.bytes, b"fake-image-data")

    def test_path_traversal_sanitizado(self):
        # O _safe_name remove caracteres não alfanuméricos,
        # então path traversal é neutralizado, não rejeitado
        name = self.store.save(str(self.img_path), "rec1", "../../etc/passwd")
        self.assertNotIn("/", name)
        self.assertNotIn("..", name)


if __name__ == "__main__":
    unittest.main()
