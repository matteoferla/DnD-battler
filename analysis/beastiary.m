%%% D&D monster analysis
%% hp vs 
% The computer does not know size ranking.
categories(categorical(size1))
%{
    'gargantuan'
    'huge'
    'large'
    'medium'
    'medium swarm of tiny'
    'small'
    'tiny'
%}
% How crazy is it that the sizes in alphabetical order are already in
% descending semantic order.
rankedsizenames = flip(categories(categorical(size1)));
rankedsize =zeros(size(size1));
for i =1:size(size1,1)
    rankedsize(i)=find(strcmp(rankedsizenames,size1(i)));
end
scatter(hp,ac,(CR+1)*9,rankedsize,'filled')
xlabel('hp')
ylabel('ac')
%set(gca,'xscale','log') %bad idea.
text(hp+12,ac,name,'FontSize',6)
title({'hp vs. ac', 'dot size based on CR', 'colored by size (blue: tiny, yellow: gargantuan)'})

% divergence of hp
figure;
ratio = log2(expected_hp./stated_hp);
scatter(stated_hp,ratio,'.')
xlabel('stated hp')
ylabel('log2FC of expectation over stated')
%{
for i =1:size(hp,1)
    if abs(ratio(i,1)) > 0.1
        text(stated_hp(i,1),ratio(i,1),name(i,1),'FontSize',6)
    end
end
%}
text(stated_hp(abs(ratio) > 0.1),ratio(abs(ratio) > 0.1),name(abs(ratio) > 0.1),'FontSize',6)
textfit(stated_hp(abs(ratio) > 0.1),ratio(abs(ratio) > 0.1),name(abs(ratio) > 0.1),'FontSize',6)
title('Divergence from prediction for hp')
line([0 700],[0 0])