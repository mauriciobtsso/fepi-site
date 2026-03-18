/* centros/static/js/admin_cep.js */
document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. MÁGICA DO CEP ---
    const cepInput = document.getElementById('id_cep');
    if (cepInput) {
        // Evento: Ao sair do campo ou colar algo
        cepInput.addEventListener('blur', function() {
            // Limpa tudo que não for número (remove pontos e traços)
            let cepLimpo = this.value.replace(/\D/g, '');
            
            // Atualiza o campo com o valor limpo
            this.value = cepLimpo;

            if (cepLimpo.length === 8) {
                // Busca na API
                fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            if(document.getElementById('id_endereco')) document.getElementById('id_endereco').value = data.logradouro;
                            if(document.getElementById('id_bairro')) document.getElementById('id_bairro').value = data.bairro;
                            if(document.getElementById('id_cidade')) document.getElementById('id_cidade').value = data.localidade;
                            if(document.getElementById('id_estado')) document.getElementById('id_estado').value = data.uf;
                            
                            // Pula para o número
                            if(document.getElementById('id_numero')) document.getElementById('id_numero').focus();
                        } else {
                            alert("CEP não encontrado na base de dados.");
                        }
                    })
                    .catch(() => console.log('Erro na busca do CEP'));
            }
        });
        
        // Permite colar qualquer sujeira que ele limpa na hora
        cepInput.addEventListener('paste', function(e) {
            setTimeout(() => {
                this.value = this.value.replace(/\D/g, '');
            }, 10);
        });
    }

    // --- 2. MÁGICA DA DATA (01011990 -> 01/01/1990) ---
    const dataInput = document.getElementById('id_data_fundacao');
    if (dataInput) {
        dataInput.placeholder = "DD/MM/AAAA";
        dataInput.addEventListener('input', function(e) {
            let v = this.value.replace(/\D/g, ''); // Só números
            
            if (v.length >= 2) v = v.substring(0,2) + '/' + v.substring(2);
            if (v.length >= 5) v = v.substring(0,5) + '/' + v.substring(5,9);
            
            this.value = v;
        });
    }
});