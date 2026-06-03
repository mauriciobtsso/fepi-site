document.addEventListener('DOMContentLoaded', function() {
    // 1. Busca de CEP via API ViaCEP
    const cepInput = document.getElementById('id_cep');
    if (cepInput) {
        cepInput.addEventListener('blur', function() {
            let cep = this.value.replace(/\D/g, '');
            if (cep.length === 8) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            document.getElementById('id_endereco').value = data.logradouro;
                            document.getElementById('id_bairro').value = data.bairro;
                            document.getElementById('id_cidade').value = data.localidade;
                            document.getElementById('id_estado').value = data.uf;
                            document.getElementById('id_numero').focus();
                        } else {
                            alert("CEP não encontrado.");
                        }
                    })
                    .catch(error => console.error("Erro ao buscar CEP:", error));
            }
        });
    }

    // 2. Máscara Simples de Telefone (Foco em UX)
    const telInput = document.getElementById('id_telefone');
    if (telInput) {
        telInput.addEventListener('input', function(e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    }
    
    // 3. Máscara Simples de CEP
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,5})(\d{0,3})/);
            e.target.value = !x[2] ? x[1] : x[1] + '-' + x[2];
        });
    }
});