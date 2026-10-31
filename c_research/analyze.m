% MATLAB/Octave analysis of C benchmark output
here = fileparts(mfilename('fullpath'));
data = jsondecode(fileread(fullfile(here,'c_sat_results.json')));
rows = data.results;
for n = 1:8
  x = rows([rows.n] == n);
  fprintf('n=%d mean_calls=%.3f max_calls=%d\n',n,mean([x.calls]),max([x.calls]));
end
% This is finite empirical evidence, not an asymptotic bound.
