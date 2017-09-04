use Makefile::GraphViz;

$parser = Makefile::GraphViz->new;
$parser->parse('MakefileVis');

# plot the tree rooted at the 'install' goal in Makefile:
$gv = $parser->plot('test');  # A GraphViz object returned.
$gv->as_png('target_test.png');