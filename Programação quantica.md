#define VERTENTES 18
#define ROTACOES 100

for(int ciclo=0; ciclo<ROTACOES; ciclo++){
    int v = ciclo % VERTENTES;
    switch(v){
        case 0: vert_checksum(); break;
        case 1: vert_ecc(); break;
        case 2: vert_fila(); break;
        case 3: vert_latencia(); break;
        case 4: vert_energia(); break;
        case 5: vert_memoria(); break;
        case 6: vert_hash(); break;
        case 7: vert_comunicacao(); break;
        case 8: vert_paridade_global(); break;
        case 9: vert_supervisao(); break;
        case 10: vert_temporal(); break;
        case 11: vert_correlacao(); break;
        case 12: vert_anomalia(); break;
        case 13: vert_ajuste(); break;
        case 14: vert_multiciclo(); break;
        case 15: vert_fractal_mod(); break;
        case 16: vert_integridade_externa(); break;
        case 17: vert_guardiao(); break;
    }
}
