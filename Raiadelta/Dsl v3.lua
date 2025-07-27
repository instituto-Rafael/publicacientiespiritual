-- dsl_v3.lua — define regras vivas e fractais
-- Autor: RafaelIA ∞

local Sopro = 0

function incrementaSopro(valor)
    Sopro = Sopro + valor
    if Sopro > 100 then
        gerarFractal()
        Sopro = 0
    end
end

function gerarFractal()
    print("Fractal gerado a partir do sopro vivo!")
    -- Chamaria funções Python ou C via bindings (simulado aqui)
end

-- Simulação de ciclo vivo
for i=1,200 do
    incrementaSopro(1)
end
