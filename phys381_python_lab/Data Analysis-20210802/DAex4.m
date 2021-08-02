%
%   Demonstration script to create some simulated data
%   and fit a polynomial to it.
%
%   Michael Albrow  June 2006
%

%
%   generate the data
%
n = 100;                   % number of data points
x = rand(1,n)*15-5;        % random x data values in range -5 to 10
xx = -5.5:0.01:10.5;       % x vector to use for plotting
p = [1 -10 -10 20];        % polynomial coefficients
y = polyval(p,x);          % y data values
sigma = rand(1,n)*25;      % random uncertainties in range 0 to 25
y = y+randn(1,n).*sigma;   % add gaussian-distributed random noise

%
%    plot the data points and the cubic polynomial
%
clf
errorbar(x,y,sigma,'r.')
hold on
plot(xx,polyval(p,xx),'m-')

%
%    fit a 4-coefficient polynomial (i.e. a cubic) to the data
%

%   create and fill the alpha and beta matrices
alpha = zeros(4,4);
beta = zeros(4,1);
for k = 1:4,
    for j = 1:4,
        alpha(k,j) = sum(x.^(4-j).*x.^(4-k)./sigma.^2);  
    end
    beta(k) = sum(y.*x.^(4-k)./sigma.^2);
end

alpha
beta
c = inv(alpha)
p                                  % the original coefficients
a = c*beta                         % the fitted coefficients
siga = sqrt(diag(c))      % uncertainties for each coefficient
plot(xx,polyval(a,xx),'b-')

chi2 = sum((y-polyval(a,x)).^2./sigma.^2)
expected_chi2 = n - 4
sigma_expected_chi2 = sqrt(2*(n-4))

% write out the data
%[xs,si] = sort(x);
%data = [x(si)' y(si)' sigma(si)']
%fid = fopen('DAex1data','w')
%fprintf(fid,'%6.3f  %8.3f  %6.3f\n',data')
%fclose(fid)



