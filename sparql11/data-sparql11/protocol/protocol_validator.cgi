#!/usr/bin/perl

use utf8;
use strict;
use warnings;
use lib qw(lib);
use Data::Dumper;
use CGI qw(Accept);
use JSON;
use TryCatch;
use Encode;
use Data::Dumper;
use HTTP::Request::Common;
use Scalar::Util qw(blessed);
use LWP::UserAgent;
use URI::Escape;
use RDF::Trine qw(statement iri literal blank);
use RDF::Trine::Namespace qw(rdf dc xsd);
use Plack;
use Plack::Request;
use Plack::Response;
use Plack::Handler::CGI;

our $VERSION	= 0.1;
our $SHOW_ERROR_DETAIL	= 1;
# our $SUBMIT_URL	= 'http://localhost/protocol_validator.cgi';
# our $SUBMIT_URL	= 'http://kasei.us/2009/09/sparql/protocol_validator.cgi';
our $SUBMIT_URL	= 'http://www.w3.org/2009/sparql/protocol_validator';

use constant {
	PASS	=> 'pass',
	FAIL	=> 'fail',
};

use constant NEGATIVE_TESTS	=> qw(
	bad_query_method
	bad_multiple_queries
	bad_query_wrong_media_type
	bad_query_missing_form_type
	bad_query_missing_direct_type
	bad_query_non_utf8
	bad_query_syntax
	bad_update_get
	bad_multiple_updates
	bad_update_wrong_media_type
	bad_update_missing_form_type
	bad_update_non_utf8
	bad_update_syntax
	bad_update_dataset_conflict
);

use constant POSITIVE_TESTS => qw(
	query_post_form
	query_get
	query_post_direct
	query_dataset_default_graph
	query_dataset_default_graphs_get
	query_dataset_default_graphs_post
	query_dataset_named_graphs_post
	query_dataset_named_graphs_get
	query_dataset_full
	query_multiple_dataset
	query_content_type_select
	query_content_type_ask
	query_content_type_describe
	query_content_type_construct
	update_dataset_default_graph
	update_dataset_default_graphs
	update_dataset_named_graphs
	update_dataset_full
	update_post_form
	update_post_direct
	update_base_uri
);

use constant REQUIRED_TESTS	=> (POSITIVE_TESTS(), NEGATIVE_TESTS());
use constant OPTIONAL_TESTS	=> ();

use constant DESCRIPTION => {
	"query_get"	=> "query via GET",
	"query_post_form"	=> "query via URL-encoded POST",
	"query_post_direct"	=> "query via POST directly",
	"query_dataset_default_graph"	=> "query with protocol-specified default graph",
	"query_dataset_default_graphs_post"	=> "POST query with protocol-specified default graphs",
	"query_dataset_default_graphs_get"	=> "GET query with protocol-specified default graphs",
	"query_dataset_named_graphs_post"	=> "POST query with protocol-specified named graphs",
	"query_dataset_named_graphs_get"	=> "GET query with protocol-specified named graphs",
	"query_dataset_full"	=> "query with protocol-specified dataset (both named and default graphs)",
	"query_multiple_dataset"	=> "query specifying dataset in both query string and protocol; test for use of protocol-specified dataset", # (test relies on the endpoint allowing client-specified RDF datasets; returns 400 otherwise)
	"query_content_type_select"	=> "SELECT query appropriate content type (expect one of: XML, JSON, CSV, TSV)",
	"query_content_type_ask"	=> "ASK query appropriate content type (expect one of: XML, JSON)",
	"query_content_type_describe"	=> "DESCRIBE query appropriate content type (expect one of: RDF/XML, Turtle, N-Triples, RDFa)",
	"query_content_type_construct"	=> "CONSTRUCT query appropriate content type (expect one of: RDF/XML, Turtle, N-Triples, RDFa)",
	"update_dataset_default_graph"	=> "update with protocol-specified default graph",
	"update_dataset_default_graphs"	=> "update with protocol-specified default graphs",
	"update_dataset_named_graphs"	=> "update with protocol-specified named graphs",
	"update_dataset_full"	=> "update with protocol-specified dataset (both named and default graphs)",
	"update_post_form"	=> "update via URL-encoded POST",
	"update_post_direct"	=> "update via POST directly",
	"update_base_uri"	=> "test for service-defined BASE URI (\"which MAY be the service endpoint\")",
	"bad_query_method"	=> "invoke query operation with a method other than GET or POST",
	"bad_multiple_queries"	=> "invoke query operation with more than one query string",
	"bad_query_wrong_media_type"	=> "invoke query operation with a POST with media type that's not url-encoded or application/sparql-query",
	"bad_query_missing_form_type"	=> "invoke query operation with url-encoded body, but without application/x-www-form-urlencoded media type",
	"bad_query_missing_direct_type"	=> "invoke query operation with SPARQL body, but without application/sparql-query media type",
	"bad_query_non_utf8"	=> "invoke query operation with direct POST, but with a non-UTF8 encoding (UTF-16)",
	"bad_query_syntax"	=> "invoke query operation with invalid query syntax (4XX result)",
	"bad_update_get"	=> "invoke update operation with GET",
	"bad_multiple_updates"	=> "invoke update operation with more than one update string",
	"bad_update_wrong_media_type"	=> "invoke update operation with a POST with media type that's not url-encoded or application/sparql-update",
	"bad_update_missing_form_type"	=> "invoke update operation with url-encoded body, but without application/x-www-form-urlencoded media type",
# 	"bad_update_missing_direct_type"	=> "invoke update operation with SPARQL body, but without application/sparql-update media type",
	"bad_update_non_utf8"	=> "invoke update operation with direct POST, but with a non-UTF8 encoding",
	"bad_update_syntax"	=> "invoke update operation with invalid update syntax (4XX result)",
	"bad_update_dataset_conflict"	=> "invoke update with both using-graph-uri/using-named-graph-uri parameter and USING/WITH clause",
};

# $XML::SAX::ParserPackage = "XML::SAX::Expat";
our $VALIDATOR_IRI	= 'http://www.w3.org/2009/sparql/protocol_validator#validator';
my $doap			= RDF::Trine::Namespace->new( 'http://usefulinc.com/ns/doap#' );
my $earl			= RDF::Trine::Namespace->new( 'http://www.w3.org/ns/earl#' );
my $sd				= RDF::Trine::Namespace->new( 'http://www.w3.org/ns/sparql-service-description#' );
my $ptests			= RDF::Trine::Namespace->new( 'http://www.w3.org/2009/sparql/docs/tests/data-sparql11/protocol/manifest#' );

binmode(\*STDOUT, ':utf8');
# if (scalar(@ARGV)) {
# 	my $q				= new CGI;
# 	$q->param('Accept' => 'text/turtle');
# 	my $qurl	= shift || '';
# 	my $uurl	= shift || '';
# 	my $res		= validate($qurl, $uurl, 1);
# 	results_response($qurl, $uurl, '#implementation#', '#name#', '#homepage#', $res, 1, $q);
# 	exit;
# }

my $app	= sub {
	my $env		= shift;
	my $req		= Plack::Request->new($env);
	my $qurl	= $req->param('query_url');
	my $uurl	= $req->param('update_url');
	my $opt		= $req->param('bp') ? 1 : 0;
	my $sw		= $req->param('software');
	my $name	= $req->param('softwarename');
	my $homepage	= $req->param('softwareurl');
	if ($homepage) {
		$homepage	= iri($homepage);
	}
	
	my $res;
	if ($qurl or $uurl) {
		$res	= validate($qurl, $uurl, $opt);
		$res	= results_response($qurl, $uurl, $sw, $name, $homepage, $res, $opt, $req);
	} else {
		$res	= $req->new_response(200);
		$res->content_type('text/html; charset=UTF-8');
		my $head	= html_header();
		my $form	= form('', '', '','','');
		my $foot	= html_footer();
		$res->body( [$head, $form, $foot] );
	}
	return $res->finalize;
};

Plack::Handler::CGI->new->run($app);

sub passed {
	my $res		= shift;
	my $test	= shift;
	my $type	= test_type($test);
	no warnings 'uninitialized';
	return ($res->{$type}{$test}{result} eq PASS);
}

sub test_messages {
	my $res		= shift;
	my $test	= shift;
	my $type	= test_type($test);
	my $msg		= $res->{$type}{$test}{message};
	if (ref($msg)) {
		return @$msg;
	} else {
		return ($msg);
	}
}

sub test_detail {
	my $res		= shift;
	my $test	= shift;
	my $type	= test_type($test);
	my $detail	= $res->{$type}{$test}{detail};
	return $detail;
}

sub test_type {
	my $test	= shift;
	foreach my $t (REQUIRED_TESTS) {
		return 'required' if ($test eq $t);
	}
	return 'optional';
}

sub add_result {
	my $res		= shift;
	my $test	= shift;
	my $status	= shift;
	my $mesg	= shift;
	my $detail	= shift;
	my $type	= test_type($test);
	my $desc	= DESCRIPTION->{ $test };
	$res->{$type}{$test}	= { result => $status, description => $desc };
	if (defined $mesg) {
		$res->{$type}{$test}{ message }	= $mesg;
	}
	if (defined $detail) {
		$res->{$type}{$test}{ detail }	= $detail;
	}
}

sub update_result {
	my $res		= shift;
	my $test	= shift;
	my $status	= shift;
	my $mesg	= shift;
	my $type	= test_type($test);
	my $desc	= DESCRIPTION->{ $test };
	if (exists($res->{$test})) {
		my $result	= $res->{$type}{$test}{result};
		if ($result eq PASS and $status eq FAIL) {
			$res->{$type}{$test}{result}	= FAIL;
		}
		if ($mesg) {
			push(@{ $res->{$type}{$test}{ message } }, $mesg);
		}
	} else {
		$res->{$type}{$test}	= { result => $status, description => $desc };
		if ($mesg) {
			$res->{$type}{$test}{ message }	= [ $mesg ];
		}
	}
}

sub validate {
	my $qurl	= shift;
	my $uurl	= shift;
	my $opt		= shift;
	my $model	= RDF::Trine::Model->new();
	my $res		= {};
	my $pass	= 0;
	
	my $ua = LWP::UserAgent->new;
	$ua->agent("SPARQL11ProtocolValidator/$VERSION " . $ua->_agent);	
	
	if (1) {
		### Positive tests
		foreach my $t (POSITIVE_TESTS) {
			try {
				my $name	= $t;
				$name		=~ tr/-/_/;
				
				unless ($qurl) {
					next if $name =~ /query/i;
				}
				unless ($uurl and $qurl) {
					next if $name =~ /update/i;
				}
				
	# 			warn "Positive test: $t\n";
				if (my $cv = __PACKAGE__->can("test_$name")) {
					$cv->($ua, $qurl, $uurl, $opt, $res, $t);
				} else {
					warn "*** no implementation for test: $name\n";
				}
			} catch ($e) {
				warn "faield test $t with error: " . Dumper($e);
			}
		}
	}
	
	if (1) {
		### Negative tests
		my @tests	= bad_requests( $qurl, $uurl );
		my %tests;
		foreach my $t (@tests) {
			try {
				my ($name, $req)	= @$t;
				unless ($qurl) {
					next if $name =~ /query/i;
				}
				unless ($uurl and $qurl) {
					next if $name =~ /update/i;
				}
				
				$tests{ $name }	= $req;
			}
		}
		
		foreach my $name (NEGATIVE_TESTS) {
			try {
				my $req		= $tests{ $name };
				warn "No request object for test $name" unless ($req);
				my $resp	= $ua->request( $req );
				my $code	= $resp->code;
				if ($code =~ /^[45]\d\d$/) {
					add_result( $res, $name, PASS );
				} else {
					add_result( $res, $name, FAIL, "Expected an error response code, but got: " . $resp->status_line, [$req, $resp] );
				}
			}
		}
	}
	
	
	return $res;
}

sub results_response {
	my $qurl	= shift;
	my $uurl	= shift;
	my $sw		= shift;
	my $name	= shift;
	my $homepage	= shift;
	my $res		= shift;
	my $opt		= shift;
	my $req		= shift;
	my @accept;
	push(@accept, { type => 'text/html', value => Accept('text/html') } );
	push(@accept, { type => 'application/json', value => Accept('application/json') } );
	push(@accept, { type => 'application/rdf+xml', value => Accept('application/rdf+xml') } );
	push(@accept, { type => 'text/turtle', value => Accept('text/turtle') } );
	push(@accept, { type => 'text/plain', value => Accept('text/plain') } );
	@accept	= sort { $b->{value} <=> $a->{value} || $b->{type} eq 'html' } @accept;
	my $a	= $accept[0];
	
	my $tested	= ($sw) ? iri($sw) : iri($qurl);
	
	my $resp	= Plack::Response->new(200);
	if ($a->{type} eq 'text/html') {
		$resp->content_type('text/html; charset=UTF-8');
		my $url	= $homepage ? $homepage->uri_value : '';
		$resp->body(html_results($qurl, $uurl, $tested->uri_value, $name, $url, $res, $opt));
	} elsif ($a->{type} eq 'application/json') {
		my $data	= { endpoint => $qurl, results => $res };
		if (length($tested)) {
			$data->{software}	= $tested;
		}
		my $type	= $a->{type};
		$resp->content_type("${type}; charset=UTF-8");
		$resp->body(JSON->new->utf8->pretty->encode($data));
	} elsif ($a->{type} =~ m#^((application/rdf[+]xml)|(text/(turtle|plain)))$#) {
		my $mediatype	= $a->{type};
		$resp->content_type("${mediatype}; charset=UTF-8");
		my $map		= RDF::Trine::NamespaceMap->new( { rdf => $rdf, earl => $earl, prot => $ptests, dc => $dc, doap => $doap } );
		my $type;
		if ($a->{type} =~ /turtle/) {
			$type	= 'turtle';
		} elsif ($a->{type} =~ /xml/) {
			$type	= 'rdfxml';
		} else {
			$type	= 'ntriples';
		}
		my $s		= RDF::Trine::Serializer->new( $type, namespaces => $map );
		$resp->body(rdf_results($qurl, $uurl, $tested, $name, $homepage, $res, $s, $opt));
	} else {
		$resp->content_type("text/plain; charset=UTF-8");
		$resp->body("should emit $a->{type}");
	}
	return $resp;
}

sub results_model {
	my $qurl	= shift;
	my $uurl	= shift;
	my $tested	= shift;
	my $name	= shift;
	my $homepage	= shift;
	my $res		= shift;
	my $s		= shift;
	my $opt		= shift;
	my $model	= RDF::Trine::Model->new();
	my ($sec, $min, $hour, $day, $mon, $year)	= gmtime();
	$mon++;
	$year	+= 1900;
	my $time	= sprintf('%04d-%02d-%02dT%02d:%02d:%02dZ', $year, $mon, $day, $hour, $min, $sec);
	my $by		= iri($VALIDATOR_IRI);
	my @tests	= (REQUIRED_TESTS);
	if ($opt) {
		push(@tests, OPTIONAL_TESTS);
	}
	
	$model->add_statement( statement($tested, $rdf->type, $doap->Project) );
	$model->add_statement( statement($tested, $doap->name, literal($name)) );
	$model->add_statement( statement($tested, $doap->homepage, $homepage) );
	
	foreach my $test (@tests) {
		unless ($qurl) {
			next if $test =~ /query/i;
		}
		unless ($uurl and $qurl) {
			next if $test =~ /update/i;
		}
		
		my $type	= test_type($test);
		my $desc	= DESCRIPTION->{ $test };
		no warnings 'uninitialized';
		my $status	= ($res->{$type}{$test}{result} eq PASS) ? $earl->pass : $earl->fail;
		
		my $a		= blank();
		my $r		= blank();
		$model->add_statement( statement($a, $rdf->type, $earl->Assertion) );
		$model->add_statement( statement($a, $earl->assertedBy, $by) );
		$model->add_statement( statement($a, $earl->subject, $tested) );
		$model->add_statement( statement($a, $earl->result, $r) );
		$model->add_statement( statement($a, $earl->test, $ptests->$test()) );
		$model->add_statement( statement($r, $rdf->type, $earl->TestResult) );
		$model->add_statement( statement($r, $earl->outcome, $status) );
		$model->add_statement( statement($r, $dc->date, literal($time, undef, $xsd->dateTime)) );
		my @msg		= test_messages($res, $test);
		foreach my $m (@msg) {
			next unless (defined($m));
			my $st	= statement($r, $earl->info, literal($m));
			$model->add_statement( $st );
		}
	}
	return $model;
}


sub rdf_results {
	my $qurl	= shift;
	my $uurl	= shift;
	my $tested	= shift;
	my $name	= shift;
	my $homepage	= shift;
	my $res		= shift;
	my $s		= shift;
	my $opt		= shift;
	my $model	= results_model($qurl, $uurl, $tested, $name, $homepage, $res, $s, $opt);
	return $s->serialize_model_to_string( $model );
}

sub html_results {
	my $qurl	= shift;
	my $uurl	= shift;
	my $tested	= shift;
	my $name	= shift;
	my $homepage	= shift;
	my $res		= shift;
	my $opt		= shift;
	my $head	= html_header();
	my $form	= form($qurl, $uurl, $tested, $name, $homepage);
	
	my $body	= $head . $form;
	
	my $req_total	= 0;
	my $req_passed	= 0;
	my $req_failed	= 0;
	foreach my $test (REQUIRED_TESTS) {
		unless ($qurl) {
			next if $test =~ /query/i;
		}
		unless ($uurl and $qurl) {
			next if $test =~ /update/i;
		}
		
		$req_total++;
		if (passed($res, $test)) {
			$req_passed++;
		} else {
			$req_failed++;
		}
	}
	
	my $opt_total	= 0;
	my $opt_passed	= 0;
	my $opt_failed	= 0;
	if ($opt) {
		foreach my $test (OPTIONAL_TESTS) {
			$opt_total++;
			if (passed($res, $test)) {
				$opt_passed++;
			} else {
				$opt_failed++;
			}
		}
	}
	
	my $total	= $req_total + $opt_total;
	my $passed	= $req_passed + $opt_passed;
	my $failed	= $req_failed + $opt_failed;
	
	my $req_class;
	if ($req_total == $req_passed) {
		$req_class	= 'pass';
	} elsif ($req_total == $req_failed) {
		$req_class	= 'fail';
	} else {
		$req_class	= 'fail';
	}
	
	my $opt_class;
	if ($opt) {
		if ($opt_total == $opt_passed) {
			$opt_class	= 'pass';
		} elsif ($opt_total == $opt_failed) {
			$opt_class	= 'fail';
		} else {
			$opt_class	= 'fail';
		}
	}
	
	my $impl	= qq[<a href="${homepage}">${name}</a>];
	
	if ($total == $passed) {
		$body	.= qq[<h1 id="summary" class="pass">All tests passed for ${impl}</h1>\n];
	} elsif ($req_total == $req_failed) {
		$body	.= qq[<h1 id="summary" class="fail">All required tests failed for ${impl}</h1>\n];
	} elsif ($req_total == $req_passed) {
		$body	.= qq[<h1 id="summary" class="warn">All required tests passed, but some tests failed for ${impl}</h1>\n];
	} else {
		$body	.= qq[<h1 id="summary" class="warn">Some tests failed for ${impl}</h1>\n];
	}
	
	$body	.= <<"END";
	<table>
		<tr>
			<th>Test</th>
			<th>Passed tests</th>
		</tr>
		<tr>
			<td><a href="#required">Required Tests</a></td>
			<td class="${req_class}">${req_passed}/${req_total}</td>
		</tr>
END
# 	if ($opt) {
# 		$body	.= <<"END";
# 		<tr>
# 			<td><a href="#optional">Best Practice Tests</a></td>
# 			<td class="${opt_class}">${opt_passed}/${opt_total}</td>
# 		</tr>
# END
# 	}

	$body	.= <<"END";
	</table>
END
	$body	.= <<"END";
	<h2 id="required">Required Tests</h2>
	<ul>
END
	foreach my $test (REQUIRED_TESTS) {
		unless ($qurl) {
			next if $test =~ /query/i;
		}
		unless ($uurl and $qurl) {
			next if $test =~ /update/i;
		}
		
		my $type	= test_type($test);
		my $desc	= "$test: " . DESCRIPTION->{ $test };
		no warnings 'uninitialized';
		my $status;
		if ($res->{$type}{$test}{result} eq PASS) {
			$status	= qq[<abbr title="pass">✔ PASS</abbr>];
		} else {
			$status	= qq[<abbr title="fail">✘ FAIL</abbr>];
		}
		my @msg		= test_messages($res, $test);
		my $msg		= scalar(@msg) ? join("<br/>", @msg) : '';
		my $detail	= test_detail($res, $test);
		
		my $class	= ($res->{$type}{$test}{result} eq PASS) ? 'pass' : 'fail';
		$body	.= <<"END";
		<li>
			<span class="${class}">${status}</span> ${desc}
END
		if ($SHOW_ERROR_DETAIL) { # XXX show failure details in html
			if (length($msg)) {
				my $reqs	= '';
				my $resps	= '';
				if (ref($detail)) {
					my ($req, $resp)	= @$detail;
					$reqs	= $req->as_string;
					$resps	= $resp->as_string;
					for ($reqs, $resps) {
						s/</&lt;/g;
						s/"/&quot;/g;
						s{\n}{<br/>\n}g;
					}
				}
				$body	.= <<"END";
				<div class="details">
					<p>$msg</p>
					<p>Request:</p>
					<p class="trace">$reqs</p>
					<p>Response:</p>
					<p class="trace">$resps</p>
				</div>
END
			}
		}
		$body	.= <<"END";
		</li>
END
	}
	$body	.= qq[\t</ul>\n];



# 	if ($opt) {
# 		$body	.= <<"END";
# 	<h2 id="required">Best Practice Tests</h2>
# 	<ul>
# END
# 		foreach my $test (OPTIONAL_TESTS) {
# 			my $type	= test_type($test);
# 			my $desc	= DESCRIPTION->{ $test };
# 			no warnings 'uninitialized';
# 			my $status	= ($res->{$type}{$test}{result} eq PASS) ? qq[<abbr title="pass">✔ PASS</abbr>] : qq[<abbr title="fail">✘ FAIL</abbr>];
# 			my @msg		= test_messages($res, $test);
# 			my $msg		= scalar(@msg) ? join("<br/>", @msg) : '';
# 			my $class	= ($res->{$type}{$test}{result} eq PASS) ? 'pass' : 'fail';
# 			$body	.= <<"END";
# 		<li>
# 			<span class="${class}">${status}</span> ${desc}
# END
# 			if (length($msg)) {
# 				$body	.= qq[\t\t\t<span class="details">$msg</span>\n];
# 			}
# 		
# 			$body	.= <<"END";
# 		</li>
# END
# 		}
# 		$body	.= qq[\t</ul>\n];
# 	}
	
	$body	.= html_footer();
	return $body;
}

sub form {
	my $qurl		= shift;
	my $uurl		= shift;
	my $software	= shift;
	my $name		= shift;
	my $homepage	= shift;
	return <<"END";
	<form action="$SUBMIT_URL" method="get"> <!-- @@ change to final W3C URI -->
		SPARQL Query Endpoint: <input name="query_url" id="query_url" type="text" size="40" value="$qurl" /><br/>
		SPARQL Update Endpoint: <input name="update_url" id="update_url" type="text" size="40" value="$uurl" /><br/>
		Implementation software IRI: <input name="software" id="software" type="text" size="40" value="$software" /><br/>
		Implementation Name: <input name="softwarename" id="softwarename" type="text" size="40" value="$name" /><br/>
		Implementation Homepage: <input name="softwareurl" id="softwareurl" type="text" size="40" value="$homepage" /><br/>
<!--		<input name="bp" id="bp" type="checkbox" value="1" /> Run best-practices tests<br/> -->
		<input name="submit" id="submit" type="submit" value="Submit" />
	</form>
END
}

sub html_header {
	return <<"END";
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<title>SPARQL Protocol Report</title>
	<style type="text/css" title="text/css">
<!--
.fail {
	color: red;
}

#summary {
	text-align: center;
}

#summary.pass {
	color: white;
	background-color: green;
}

#summary.warn {
	color: white;
	background-color: orange;
}

#summary.fail {
	color: white;
	background-color: red;
}

.pass {
	color: green;
}

.trace {
	border: 1px solid #aaa;
	padding: 5px;
	overflow: scroll;
}

.details {
	display: block;
	width: 75%;
	border: 1px dashed #000;
	padding: 2px 1em;
	background-color: #ffa;
}

table {
	width: 100%;
	border-collapse: collapse;
}

th {
	border-bottom: 3px double #000;
}

td {
	border: 1px solid #999;
}

-->
</style>
</head>
<body>
END
}

sub html_footer {
	return <<"END";
</body>
</html>
END
}

sub _positive_test_request {
	my ($ua, $res, $name, $req)	= @_;
	my $resp	= $ua->request( $req );
# 	warn $resp->status_line;
	if ($resp->is_success) {
		return $resp;
	} else {
		add_result( $res, $name, FAIL, "Expected success response code, but got: " . $resp->status_line, [$req, $resp] );
		return;
	}
}

sub _test_boolean_result_for_true {
	my ($req, $resp, $res, $name)	= @_;
	my $type	= $resp->header('Content-Type');
	my $content	= $resp->decoded_content;
	my $iter	= ($type =~ /xml/) ? RDF::Trine::Iterator->from_string($content) : RDF::Trine::Iterator->from_json($content);
	my $r		= $iter->next;
	if ($r) {
		add_result( $res, $name, PASS );
	} else {
		add_result( $res, $name, FAIL, "Expected true SPARQL boolean result, but got false", [$req, $resp] );
	}
}

sub _test_result_for_select_query {
	my ($req, $resp, $res, $name)	= @_;
	my $type	= $resp->header('Content-Type');
	if (_test_for_media_type($type, 'application/sparql-results+xml')) {
		add_result( $res, $name, PASS );
	} elsif (_test_for_media_type($type, 'application/sparql-results+json')) {
		add_result( $res, $name, PASS );
	} elsif ($type =~ m#text/tab-separated-values#) {
		add_result( $res, $name, PASS );
	} elsif ($type =~ m#text/csv#) {
		add_result( $res, $name, PASS );
	} else {
		add_result( $res, $name, FAIL, "Expected SPARQL Results format appropriate for SELECT form, but got $type", [$req, $resp] );
	}
}

sub _test_result_for_ask_query {
	my ($req, $resp, $res, $name)	= @_;
	Carp::confess unless (blessed($resp) and $resp->can('header'));
	my $type	= $resp->header('Content-Type');
	if (_test_for_media_type($type, 'application/sparql-results+xml')) {
		add_result( $res, $name, PASS );
	} elsif (_test_for_media_type($type, 'application/sparql-results+json')) {
		add_result( $res, $name, PASS );
	} else {
		add_result( $res, $name, FAIL, "Expected SPARQL Results format appropriate for ASK form, but got $type", [$req, $resp] );
	}
}

sub _test_result_for_rdf_type {
	my ($req, $resp, $res, $name)	= @_;
	my $type	= $resp->header('Content-Type');
	
	# RDF/XML, Turtle, N-Triples, RDFa
	if ($type =~ m#^((application/rdf[+](xml|json))|(text/turtle))#) {
		add_result( $res, $name, PASS );
		# XXX @@
	} else {
		add_result( $res, $name, FAIL, "Expected RDF Results format, but got $type", [$req, $resp] );
	}
}

sub _test_for_media_type {
	my $got		= shift;
	my $expect	= shift;
# 	warn "testing media type $got...\n";
	my $re		= quotemeta($expect);
	return ($got =~ m{^${re}(?:\s*;\s*charset=.*)?$});
}

sub __________TESTS__________ {}

sub bad_requests {
	my $qurl	= shift;
	my $uurl	= shift;
	
	my @reqs;
	
	if ($qurl) {
		{
			# bad-query-method - invoke query operation with a method other than GET or POST
			my $req	= PUT("${qurl}?query=ASK%20%7B%7D&default-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata0.rdf", Content => '');
			push(@reqs, [ 'bad_query_method', $req]);
		}
	
		{
			#  bad-multiple-queries - invoke query operation with more than one query string
			my $req	= GET("${qurl}?query=ASK%20%7B%7D&query=SELECT%20%2A%20%7B%7D&default-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata0.rdf");
			push(@reqs, [ 'bad_multiple_queries', $req]);
		}
	
		{
			#  bad-query-wrong-media-type - invoke query operation with a POST with media type that's not url-encoded or application/sparql-query
			my $req	= POST($qurl, ['default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf'], 'Content-Type' => 'text/plain', Content => 'ASK {}');
			push(@reqs, [ 'bad_query_wrong_media_type', $req]);
		}
	
		{
			#  bad-query-missing-form-type - invoke query operation with url-encoded body, but without application/x-www-form-urlencoded media type
			my $req	= POST($qurl, ['query' => 'ASK {}', 'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf']);
			$req->remove_header('Content-Type');
			push(@reqs, [ 'bad_query_missing_form_type', $req]);
		}
	
		{
			#  bad-query-missing-direct-type - invoke query operation with SPARQL body, but without application/sparql-query media type
			my $req	= HTTP::Request->new('POST', $qurl, ['default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf']);
			$req->content('ASK {}');
			push(@reqs, [ 'bad_query_missing_direct_type', $req]);
		}
	
		{
			#  bad-query-non-utf8 - invoke query operation with direct POST, but with a non-UTF8 encoding (UTF-16)
			my $req	= POST($qurl, ['default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf'], 'Content-Type' => 'application/sparql-query; charset=UTF-16', Content => encode('utf-16', 'ASK {}'));
			push(@reqs, [ 'bad_query_non_utf8', $req]);
		}
	
		{
			#  bad-query-syntax - invoke query operation with invalid query syntax (4XX result)
			my $req	= GET("${qurl}?query=ASK%20%7B&default-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata0.rdf");
			push(@reqs, [ 'bad_query_syntax', $req]);
		}
	}
	
	if ($uurl) {
		{
			#  bad-update-get - invoke update operation with GET
			my $req	= GET("${uurl}?update=CLEAR%20ALL&using-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata0.rdf");
			push(@reqs, [ 'bad_update_get', $req]);
		}
	
		{
			#  bad-multiple-updates - invoke update operation with more than one update string
			my $req	= POST($uurl, [ 'update' => 'CLEAR NAMED', 'update' => 'CLEAR DEFAULT', 'using-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf' ]);
			push(@reqs, [ 'bad_multiple_updates', $req]);
		}
	
		{
			#  bad-update-wrong-media-type - invoke update operation with a POST with media type that's not url-encoded or application/sparql-update
			my $req	= POST($uurl, ['using-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf'], 'Content-Type' => 'text/plain', Content => 'CLEAR NAMED');
			push(@reqs, [ 'bad_update_wrong_media_type', $req]);
		}
	
		{
			#  bad-update-missing-form-type - invoke update operation with url-encoded body, but without application/x-www-form-urlencoded media type
			my $req	= POST($uurl, [ 'update' => 'CLEAR NAMED', 'using-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf' ]);
			$req->remove_header('Content-Type');
			push(@reqs, [ 'bad_update_missing_form_type', $req]);
		}
	
# 		{
# 			#  bad-update-missing-direct-type - invoke update operation with SPARQL body, but without application/sparql-update media type
# 			my $req	= POST($uurl, ['using-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf'], Content => 'CLEAR NAMED');
# 			$req->remove_header('Content-Type');
# 			push(@reqs, [ 'bad_update_missing_direct_type', $req]);
# 		}
	
		{
			#  bad-update-non-utf8 - invoke update operation with direct POST, but with a non-UTF8 encoding
			my $req	= POST($uurl, ['using-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf'], 'Content-Type' => 'application/sparql-update; charset=UTF-16', Content => encode('utf-16', 'CLEAR NAMED'));
			push(@reqs, [ 'bad_update_non_utf8', $req]);
		}
	
		{
			#  bad-update-syntax - invoke update operation with invalid update syntax (4XX result)
			my $req	= POST($uurl, ['update' => 'CLEAR XYZ', 'using-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf']);
			push(@reqs, [ 'bad_update_syntax', $req]);
		}
	
		{
			#  bad-update-dataset-conflict - invoke update with both using-graph-uri/using-named-graph-uri parameter and USING/WITH clause
			my $update	= <<"END";
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
WITH <http://example/addresses>
DELETE { ?person foaf:givenName 'Bill' }
INSERT { ?person foaf:givenName 'William' }
WHERE {
	?person foaf:givenName 'Bill'
}
END
			my $req	= POST($uurl, ['using-named-graph-uri' => 'http://example/people', 'update' => $update]);
			push(@reqs, [ 'bad_update_dataset_conflict', $req]);
		}
	}

	return @reqs;
}

sub test_query_get {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= GET("${qurl}?query=ASK%20%7B%7D&default-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata0.rdf");
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );

		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_post_form {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($qurl, ['query' => 'ASK {}', 'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf']);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_post_direct {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($qurl, ['default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf'], 'Content-Type' => 'application/sparql-query', Content => 'ASK {}');
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub _setup_dataset {
	my $ua		= shift;
	my $uurl	= shift;
	my $res		= shift;
	my $name	= shift;
	my $dgraphs	= shift;
	my $graphs	= shift;
	my @ops		= ('DROP ALL');
	foreach my $g (@$dgraphs) {
		push(@ops, "LOAD <$g>");
	}
	foreach my $g (@$graphs) {
		push(@ops, "LOAD <$g> INTO GRAPH <$g>");
	}
	my $sparql	= join(" ;\n", @ops);
	my $req		= POST($uurl, [
					'update' => $sparql,
				]);
	my $resp	= $ua->request( $req );
	if ($resp->is_success) {
		return 1;
	} else {
		add_result( $res, $name, FAIL, "Failed to setup dataset; " . $resp->status_line, [$req, $resp] );
		return;
	}
}

sub test_query_dataset_default_graph {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	_setup_dataset($ua, $uurl, $res, $name, [], ['http://kasei.us/2009/09/sparql/data/data1.rdf']) or return;
	my $req		= POST($qurl, [
					'query' => 'ASK { <http://kasei.us/2009/09/sparql/data/data1.rdf> ?p ?o }',
					'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data1.rdf'
				]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_dataset_default_graphs_post {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	_setup_dataset($ua, $uurl, $res, $name, [], ['http://kasei.us/2009/09/sparql/data/data1.rdf', 'http://kasei.us/2009/09/sparql/data/data2.rdf']) or return;
	my $req		= POST($qurl, [
					'query' => 'ASK { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type . <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type . }',
					'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data1.rdf',
					'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data2.rdf'
				]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_dataset_default_graphs_get {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	_setup_dataset($ua, $uurl, $res, $name, [], ['http://kasei.us/2009/09/sparql/data/data1.rdf', 'http://kasei.us/2009/09/sparql/data/data2.rdf']) or return;
	my $req		= GET("${qurl}?query=ASK%20%7B%20%3Chttp%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf%3E%20a%20%3Ftype%20.%20%3Chttp%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata2.rdf%3E%20a%20%3Ftype%20.%20%7D&default-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf&default-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata2.rdf");
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_dataset_named_graphs_post {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	_setup_dataset($ua, $uurl, $res, $name, [], ['http://kasei.us/2009/09/sparql/data/data1.rdf', 'http://kasei.us/2009/09/sparql/data/data2.rdf']) or return;
	my $req		= POST($qurl, [
					'query' => 'ASK { GRAPH ?g1 { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type } GRAPH ?g2 { <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type } }',
					'named-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data1.rdf',
					'named-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data2.rdf'
				]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_dataset_named_graphs_get {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	_setup_dataset($ua, $uurl, $res, $name, [], ['http://kasei.us/2009/09/sparql/data/data1.rdf', 'http://kasei.us/2009/09/sparql/data/data2.rdf']) or return;
	my $req		= GET("${qurl}?query=ASK%20%7B%20GRAPH%20%3Fg1%20%7B%20%3Chttp%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf%3E%20a%20%3Ftype%20%7D%20GRAPH%20%3Fg2%20%7B%20%3Chttp%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata2.rdf%3E%20a%20%3Ftype%20%7D%20%7D&named-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf&named-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata2.rdf");
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_dataset_full {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	_setup_dataset($ua, $uurl, $res, $name, [], ['http://kasei.us/2009/09/sparql/data/data1.rdf', 'http://kasei.us/2009/09/sparql/data/data2.rdf', 'http://kasei.us/2009/09/sparql/data/data3.rdf']) or return;
	my $query	= <<"END";
ASK {
	<http://kasei.us/2009/09/sparql/data/data3.rdf> a ?type
	GRAPH ?g1 { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type }
	GRAPH ?g2 { <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type }
}
END
	my $req		= POST($qurl, [
					'query' => $query,
					'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data3.rdf',
					'named-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data1.rdf',
					'named-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data2.rdf'
				]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_multiple_dataset {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	_setup_dataset($ua, $uurl, $res, $name, [], ['http://kasei.us/2009/09/sparql/data/data1.rdf', 'http://kasei.us/2009/09/sparql/data/data2.rdf', 'http://kasei.us/2009/09/sparql/data/data3.rdf']) or return;
	my $req		= POST($qurl, [
					'query' => 'ASK FROM <http://kasei.us/2009/09/sparql/data/data3.rdf> { GRAPH ?g1 { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type } GRAPH ?g2 { <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type } }',
					'named-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data1.rdf',
					'named-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data2.rdf'
				]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		if (_test_for_media_type($type, 'application/sparql-results+xml') or _test_for_media_type($type, 'application/sparql-results+json')) {
			_test_boolean_result_for_true( $req, $resp, $res, $name );
		} else {
			add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
		}
	}
}

sub test_query_content_type_select {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($qurl, [ 'query' => 'SELECT (1 AS ?value) {}', 'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf' ]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		_test_result_for_select_query( $req, $resp, $res, $name );
	}
}

sub test_query_content_type_ask {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($qurl, [ 'query' => 'ASK {}', 'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf' ]);
# 	warn $req->as_string;
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
# 		warn $resp->as_string;
		my $type	= $resp->header('Content-Type');
		_test_result_for_ask_query( $req, $resp, $res, $name );
	}
}

sub test_query_content_type_describe {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($qurl, [ 'query' => 'DESCRIBE <http://example.org/>', 'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf' ]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		_test_result_for_rdf_type( $req, $resp, $res, $name );
	}
}

sub test_query_content_type_construct {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($qurl, [ 'query' => 'CONSTRUCT { <s> <p> 1 } WHERE {}', 'default-graph-uri' => 'http://kasei.us/2009/09/sparql/data/data0.rdf' ]);
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $type	= $resp->header('Content-Type');
		_test_result_for_rdf_type( $req, $resp, $res, $name );
	}
}

sub __________UPDATE_TESTS__________ {}

sub test_update_post_form {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($uurl, [
					'update' => 'CLEAR ALL',
				]);
	my $resp	= $ua->request( $req );
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		add_result( $res, $name, PASS );
	}
}

sub test_update_post_direct {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	my $req		= POST($uurl, [], 'Content-Type' => 'application/sparql-update', Content => 'CLEAR ALL');
	my $resp	= $ua->request( $req );
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		add_result( $res, $name, PASS );
	}
}

sub test_update_base_uri {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	{
		my $resp	= $ua->request( POST($uurl, [
						'update' => 'CLEAR SILENT GRAPH <http://example.org/protocol-base-test/> ; INSERT DATA { GRAPH <http://example.org/protocol-base-test/> { <http://example.org/s> <http://example.org/p> <test> } }',
					]) );
	}
	my $req	= POST($qurl, [
						'query' => 'SELECT ?o WHERE { GRAPH <http://example.org/protocol-base-test/> { <http://example.org/s> <http://example.org/p> ?o } }'
					], 'Accept' => 'application/sparql-results+xml');
	if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
		my $content	= $resp->decoded_content;
		my $iter	= RDF::Trine::Iterator->from_string($content);
		my $row		= blessed($iter) ? $iter->next : {};
		my $term	= $row->{'o'};
		if (blessed($term)) {
			my $uri	= $term->uri_value;
			if ($uri eq 'test') {
				add_result( $res, $name, FAIL, "No BASE URI was applied to inserted data", [$req, $resp] );
			} else {
				add_result( $res, $name, PASS );
			}
		} else {
			add_result( $res, $name, FAIL, "Failed to retrieve inserted data with subsequent query", [$req, $resp] );
		}
	}
}

sub test_update_dataset_default_graph {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	{
		my $sparql	= <<"END";
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
CLEAR ALL ;
INSERT DATA {
	GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> {
		<http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document
	}
} ;
INSERT {
	GRAPH <http://example.org/protocol-update-dataset-test/> {
		?s a dc:BibliographicResource
	}
}
WHERE {
	?s a foaf:Document
}
END
		my $req		= POST("${uurl}?using-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf", [
						'update' => $sparql,
					]);
		return unless (my $resp = _positive_test_request($ua, $res, $name, $req));
	}
	
	if (0) {
		my $sparql      = "SELECT * WHERE { GRAPH ?g { ?s ?p ?o } }";
		my $req         = POST($qurl, [], 'Content-Type' => 'application/sparql-query', 'Accept' => 'application/sparql-results+xml', Content => $sparql);
		my $resp = _positive_test_request($ua, $res, $name, $req);
		warn $resp->decoded_content;
		die;
	}
	
	{
		my $sparql	= <<"END";
ASK {
	GRAPH <http://example.org/protocol-update-dataset-test/> {
		<http://kasei.us/2009/09/sparql/data/data1.rdf> a <http://purl.org/dc/terms/BibliographicResource>
	}
}
END
		my $req		= POST($qurl, [], 'Content-Type' => 'application/sparql-query', 'Accept' => 'application/sparql-results+xml', Content => $sparql);
		if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
			my $xmlres	= $resp->decoded_content;
			my $type	= $resp->header('Content-Type');
			if (_test_for_media_type($type, 'application/sparql-results+xml')) {
				_test_boolean_result_for_true( $req, $resp, $res, $name );
			} else {
				add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
			}
		}
	}
}

sub test_update_dataset_default_graphs {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	{
		my $sparql	= <<"END";
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
DROP ALL ;
INSERT DATA {
	GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> { <http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document }
	GRAPH <http://kasei.us/2009/09/sparql/data/data2.rdf> { <http://kasei.us/2009/09/sparql/data/data2.rdf> a foaf:Document }
	GRAPH <http://kasei.us/2009/09/sparql/data/data3.rdf> { <http://kasei.us/2009/09/sparql/data/data3.rdf> a foaf:Document }
} ;
INSERT {
	GRAPH <http://example.org/protocol-update-dataset-graphs-test/> {
		?s a dc:BibliographicResource
	}
}
WHERE {
	?s a foaf:Document
}
END
		my $req		= POST("${uurl}?using-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf&using-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata2.rdf", [
						'update' => $sparql,
					]);
		return unless (my $resp = _positive_test_request($ua, $res, $name, $req));
	}
	
	{
		my $sparql	= <<"END";
ASK {
	GRAPH <http://example.org/protocol-update-dataset-graphs-test/> {
		<http://kasei.us/2009/09/sparql/data/data1.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
		<http://kasei.us/2009/09/sparql/data/data2.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
	}
	FILTER NOT EXISTS {
		GRAPH <http://example.org/protocol-update-dataset-graphs-test/> {
			<http://kasei.us/2009/09/sparql/data/data3.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
		}
	}
}
END
		my $req		= POST($qurl, [], 'Content-Type' => 'application/sparql-query', 'Accept' => 'application/sparql-results+xml', Content => $sparql);
		if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
			my $xmlres	= $resp->decoded_content;
			my $type	= $resp->header('Content-Type');
			if (_test_for_media_type($type, 'application/sparql-results+xml')) {
				_test_boolean_result_for_true( $req, $resp, $res, $name );
			} else {
				add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
			}
		}
	}
}

sub test_update_dataset_named_graphs {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	{
		my $sparql	= <<"END";
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
DROP ALL ;
INSERT DATA {
	GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> { <http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document }
	GRAPH <http://kasei.us/2009/09/sparql/data/data2.rdf> { <http://kasei.us/2009/09/sparql/data/data2.rdf> a foaf:Document }
	GRAPH <http://kasei.us/2009/09/sparql/data/data3.rdf> { <http://kasei.us/2009/09/sparql/data/data3.rdf> a foaf:Document }
} ;
INSERT {
	GRAPH <http://example.org/protocol-update-dataset-named-graphs-test/> {
		?s a dc:BibliographicResource
	}
}
WHERE {
	GRAPH ?g {
		?s a foaf:Document
	}
}
END
		my $req		= POST("${uurl}?using-named-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf&using-named-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata2.rdf", [
						'update' => $sparql,
					]);
		return unless (my $resp = _positive_test_request($ua, $res, $name, $req));
	}
	
	{
		my $sparql	= <<"END";
ASK {
	GRAPH <http://example.org/protocol-update-dataset-named-graphs-test/> {
		<http://kasei.us/2009/09/sparql/data/data1.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
		<http://kasei.us/2009/09/sparql/data/data2.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
	}
	FILTER NOT EXISTS {
		GRAPH <http://example.org/protocol-update-dataset-named-graphs-test/> {
			<http://kasei.us/2009/09/sparql/data/data3.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
		}
	}
}
END
		my $req		= POST($qurl, [], 'Content-Type' => 'application/sparql-query', 'Accept' => 'application/sparql-results+xml', Content => $sparql);
		if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
			my $xmlres	= $resp->decoded_content;
			my $type	= $resp->header('Content-Type');
			if (_test_for_media_type($type, 'application/sparql-results+xml')) {
				_test_boolean_result_for_true( $req, $resp, $res, $name );
			} else {
				add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
			}
		}
	}
}

sub test_update_dataset_full {
	my ($ua, $qurl, $uurl, $opt, $res, $name)	= @_;
	{
		my $sparql	= <<"END";
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
DROP ALL ;
INSERT DATA {
	GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> { <http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document }
	GRAPH <http://kasei.us/2009/09/sparql/data/data2.rdf> { <http://kasei.us/2009/09/sparql/data/data2.rdf> a foaf:Document }
	GRAPH <http://kasei.us/2009/09/sparql/data/data3.rdf> { <http://kasei.us/2009/09/sparql/data/data3.rdf> a foaf:Document }
} ;
INSERT {
	GRAPH <http://example.org/protocol-update-dataset-full-test/> {
		?s <http://example.org/in> ?in
	}
}
WHERE {
	{
		GRAPH ?g { ?s a foaf:Document }
		BIND(?g AS ?in)
	}
	UNION
	{
		?s a foaf:Document .
		BIND("default" AS ?in)
	}
}
END
		my $req		= POST("${uurl}?using-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata1.rdf&using-named-graph-uri=http%3A%2F%2Fkasei.us%2F2009%2F09%2Fsparql%2Fdata%2Fdata2.rdf", [
						'update' => $sparql,
					]);
		return unless (my $resp = _positive_test_request($ua, $res, $name, $req));
	}
	
	{
		my $sparql	= <<"END";
ASK {
	GRAPH <http://example.org/protocol-update-dataset-full-test/> {
		<http://kasei.us/2009/09/sparql/data/data1.rdf> <http://example.org/in> "default" .
		<http://kasei.us/2009/09/sparql/data/data2.rdf> <http://example.org/in> <http://kasei.us/2009/09/sparql/data/data2.rdf> .
	}
	FILTER NOT EXISTS {
		GRAPH <http://example.org/protocol-update-dataset-full-test/> {
			<http://kasei.us/2009/09/sparql/data/data3.rdf> ?p ?o
		}
	}
}
END
		my $req		= POST($qurl, [], 'Content-Type' => 'application/sparql-query', 'Accept' => 'application/sparql-results+xml', Content => $sparql);
		if (my $resp = _positive_test_request($ua, $res, $name, $req)) {
			my $xmlres	= $resp->decoded_content;
			my $type	= $resp->header('Content-Type');
			if (_test_for_media_type($type, 'application/sparql-results+xml')) {
				_test_boolean_result_for_true( $req, $resp, $res, $name );
			} else {
				add_result( $res, $name, FAIL, "Expected SPARQL XML or JSON results, but got: " . $type, [$req, $resp] );
			}
		}
	}
}

__END__