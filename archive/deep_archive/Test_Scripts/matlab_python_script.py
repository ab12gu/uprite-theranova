import matlab.engine

eng = matlab.engine.start_matlab()
eng.mat_file_visual(nargout=0)
