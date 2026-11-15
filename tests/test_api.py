from app.main import create_app


def make_client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_health_and_version(tmp_path):
    client = make_client(tmp_path)

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.get_json()["status"] == "ok"

    res_version = client.get("/version")
    assert res_version.status_code == 200
    assert "version" in res_version.get_json()


def test_crud_and_filter_tasks(tmp_path):
    client = make_client(tmp_path)

    # Criar duas tarefas
    res1 = client.post("/tasks", json={"title": "Estudar AWS"})
    assert res1.status_code == 201
    t1 = res1.get_json()

    res2 = client.post("/tasks", json={"title": "Configurar CI/CD"})
    assert res2.status_code == 201
    t2 = res2.get_json()

    # Concluir a primeira
    patch_res = client.patch(f"/tasks/{t1['id']}", json={"done": True})
    assert patch_res.status_code == 200

    # Filtrar por done=true e done=false
    done_true = client.get("/tasks?done=true").get_json()
    assert len(done_true) == 1
    assert done_true[0]["id"] == t1["id"]

    done_false = client.get("/tasks?done=false").get_json()
    assert len(done_false) == 1
    assert done_false[0]["id"] == t2["id"]

    # Filtro invalido retorna 400
    bad_filter = client.get("/tasks?done=talvez")
    assert bad_filter.status_code == 400

    # Excluir tarefa e confirmar 404 em seguida
    del_res = client.delete(f"/tasks/{t1['id']}")
    assert del_res.status_code == 204

    del_again = client.delete(f"/tasks/{t1['id']}")
    assert del_again.status_code == 404
