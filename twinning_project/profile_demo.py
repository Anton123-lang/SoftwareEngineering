import cProfile, pstats, io
from generator import generate_exercises

pr = cProfile.Profile()
pr.enable()
generate_exercises(10000, 20)   # 生成一万道题
pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(15)
print(s.getvalue())