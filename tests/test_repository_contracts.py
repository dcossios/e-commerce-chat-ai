from src.domain.repositories import IChatRepository, IProductRepository


def test_product_repository_contract_methods_are_declared():
    assert IProductRepository.get_all(None) is None
    assert IProductRepository.get_by_id(None, 1) is None
    assert IProductRepository.get_by_brand(None, "Nike") is None
    assert IProductRepository.get_by_category(None, "Running") is None
    assert IProductRepository.save(None, None) is None
    assert IProductRepository.delete(None, 1) is None


def test_chat_repository_contract_methods_are_declared():
    assert IChatRepository.save_message(None, None) is None
    assert IChatRepository.get_session_history(None, "s1", None) is None
    assert IChatRepository.delete_session_history(None, "s1") is None
    assert IChatRepository.get_recent_messages(None, "s1", 3) is None
