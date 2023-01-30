// Source header
#include "Relations.hpp"

#define BUILD_PRAGMA_TOKEN "build"
#define LINK_PRAGMA_TOKEN "link"
#define INCLUDE_TOKEN "include"

namespace QED::Pragmatic
{
	BuildPragma::BuildPragma() : PragmaHandler(BUILD_PRAGMA_TOKEN, {{}, {true}, {true}}, 1) { }

	bool BuildPragma::CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation)
	{
		std::string sourceInput = tokens[1];
		std::string objectOutput = tokens.size() == 3 ? tokens[2] : Replace(tokens[1], ".cpp", ".o"); // TODO: check tokens[1] for ending with ".cpp"
		
		// Get meta & save object file as node & create connection between source and object file
		Meta::Node(sourceFileDir + objectOutput, sourceFilePath);
		Meta::Node(sourceFileDir + sourceInput, sourceFilePath);

		// Add edge if not already in meta
		Meta::Edge(sourceInput, objectOutput, BUILD_PRAGMA_TOKEN, sourceFilePath);

		return true;
	}

	std::string BuildPragma::Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics)
	{
		return "";
	}

	LinkPragma::LinkPragma() : PragmaHandler(LINK_PRAGMA_TOKEN, {{}, {true}, {true}}, 1) { }

	bool LinkPragma::CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation)
	{
		std::string objectInput = tokens.size() == 3 ? tokens[1] : sourceFilePath; // TODO: search graph from sourceFilePath to object files
		std::string binaryOutput = tokens.size() == 3 ? tokens[2] : tokens[1];
		
		// Get meta & save object file as node & create connection between source and object file
		Meta::Node(objectInput, sourceFilePath);
		Meta::Node(binaryOutput, sourceFilePath);

		// Add edge if not already in meta
		Meta::Edge(objectInput, binaryOutput, LINK_PRAGMA_TOKEN, sourceFilePath);
		
		return true;
	}

	std::string LinkPragma::Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics)
	{
		return "";
	}
	
	void IncludeCallback(std::string source, std::string target)
	{
		// Get meta & save object file as node & create connection between source and object file
		Meta::Node(source, source);
		Meta::Node(target, source);

		// Add edge if not already in meta
		Meta::Edge(source, target, INCLUDE_TOKEN, source);
	}
} // namespace QED::Pragmatic