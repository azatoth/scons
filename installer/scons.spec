import os.path

base_scripts = [os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py')]
scons_script = os.path.join('build', 'scons', 'script', 'scons')
scons_engine_dir = os.path.join('build', 'scons', 'engine')
hooks_dir = os.path.join('build', 'installer', 'hooks')

scons_analysis = Analysis(base_scripts + [scons_script], pathex = [scons_engine_dir], hookspath = [hooks_dir])
scons_pyz = PYZ(scons_analysis.pure)
scons_exe = EXE(scons_analysis.scripts, scons_pyz, name = 'scons.exe', console = 1, exclude_binaries = 1)

coll = COLLECT(
                scons_exe,
                scons_analysis.binaries,
                scons_analysis.zipfiles,
                scons_analysis.datas,
                name = os.path.join('dist'),
              )