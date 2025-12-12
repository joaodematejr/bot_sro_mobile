#!/usr/bin/env python3
"""
Busca automática do melhor deslocamento (x,y) para `posicao_minimapa` baseado
na média de pixels detectados nas imagens de `treino_ml`.

Ele testa uma grade de offsets em relação à posição atual e escolhe o
deslocamento que maximiza a média dos `total` retornados por
`evaluate_minimap_dataset.analyze_image`.

Uso:
  python3 search_minimap_offset.py --input-dir treino_ml --steps 7 --step-size 10

Ao final, atualiza `config_farming_adb.json` com a nova posição encontrada e
salva um CSV com os resultados por offset.
"""
import os
import json
import argparse
import glob
import statistics
from evaluate_minimap_dataset import load_config, analyze_image


def evaluate_for_offset(cfg, images, out_dir, dx, dy, mode_opts=None):
    # modify a copy of cfg
    cfg2 = dict(cfg)
    pos = dict(cfg2['posicao_minimapa'])
    pos['x'] = int(pos['x'] + dx)
    pos['y'] = int(pos['y'] + dy)
    cfg2['posicao_minimapa'] = pos

    totals = []
    # run analyze_image but don't save annotated images to speed up: pass out_dir=None
    for img in images:
        try:
            r = analyze_image(img, cfg2, save_annot=False, out_dir=None, **(mode_opts or {}))
            totals.append(r['total'])
        except Exception:
            totals.append(0)

    mean_total = statistics.mean(totals) if totals else 0.0
    median = statistics.median(totals) if totals else 0.0
    return {'dx': dx, 'dy': dy, 'mean': mean_total, 'median': median, 'samples': len(totals)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', default='treino_ml')
    parser.add_argument('--config', default='config_farming_adb.json')
    parser.add_argument('--out-csv', default='debug_eval_offset/results_offsets.csv')
    parser.add_argument('--steps', type=int, default=7, help='Número de passos por dimensão (odd)')
    parser.add_argument('--step-size', type=int, default=10, help='Pixels por passo')
    parser.add_argument('--mode', choices=['rgb','hsv'], default='hsv')
    parser.add_argument('--h_tol', type=int, default=10)
    parser.add_argument('--s_tol', type=int, default=60)
    parser.add_argument('--v_tol', type=int, default=60)
    args = parser.parse_args()

    cfg = load_config(args.config)

    images = sorted(glob.glob(os.path.join(args.input_dir, '*.png')) + glob.glob(os.path.join(args.input_dir, '*.jpg')))
    if not images:
        print('Nenhuma imagem encontrada em', args.input_dir)
        return

    # center offset range
    steps = args.steps if args.steps % 2 == 1 else args.steps + 1
    half = steps // 2
    shifts = [ (i - half) * args.step_size for i in range(steps) ]

    results = []
    mode_opts = {'mode': args.mode, 'h_tol': args.h_tol, 's_tol': args.s_tol, 'v_tol': args.v_tol} if args.mode == 'hsv' else {'mode':'rgb'}

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)

    print(f'Testando offsets (dx,dy) em grid {len(shifts)}x{len(shifts)} centered at current pos...')
    for dx in shifts:
        for dy in shifts:
            res = evaluate_for_offset(cfg, images, None, dx, dy, mode_opts=mode_opts)
            results.append(res)
            print(f"dx={dx:+d} dy={dy:+d} mean={res['mean']:.2f} median={res['median']:.1f}")

    # choose best by mean
    best = max(results, key=lambda r: r['mean'])
    print('\nMelhor offset encontrado:', best)

    # write csv
    import csv
    with open(args.out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['dx','dy','mean','median','samples'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # apply best offset to config and save
    pos = cfg['posicao_minimapa']
    pos['x'] = int(pos['x'] + best['dx'])
    pos['y'] = int(pos['y'] + best['dy'])
    cfg['posicao_minimapa'] = pos
    with open(args.config, 'w') as f:
        json.dump(cfg, f, indent=2)

    print('Config atualizada em', args.config)
    print('CSV de offsets salvo em', args.out_csv)


if __name__ == '__main__':
    main()
