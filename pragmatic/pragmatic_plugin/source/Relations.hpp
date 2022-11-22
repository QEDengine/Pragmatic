#pragma once

// Standard library
#include <string>
#include <vector>

// Clang
#include "clang/Basic/Diagnostic.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Lex/Preprocessor.h"
#include "clang/Basic/LangStandard.h"

// Pragmatic
#include "PragmaHandler.hpp"
#include "Utility.hpp"

#define OBJECT_PRAGMA_TOKEN "object"
#define LINK_PRAGMA_TOKEN "link"
#define SOURCE_PRAGMA_TOKEN "source"

namespace QED { namespace Pragmatic
{

	class ObjectPragma : public PragmaHandler
	{
		public:
		ObjectPragma() : PragmaHandler(OBJECT_PRAGMA_TOKEN, {{}, {true}, {true}}, 1) { }

		public:
		virtual bool CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation) override
		{
			std::string sourceInput = tokens[1];
			std::string objectOutput = tokens.size() == 3 ? tokens[2] : Replace(tokens[1], ".cpp", ".o"); // TODO: check tokens[1] for ending with ".cpp"
			
			// Get meta & save object file as node & create connection between source and object file
			auto& meta = Meta::GetInstance(preprocessor);
			meta.json["graph"]["nodes"][sourceFileDir + objectOutput]["metadata"]["defined"] = sourceFilePath;
			meta.json["graph"]["edges"].push_back
			({
				{"source", sourceInput},
				{"target", objectOutput},
				{"relation", OBJECT_PRAGMA_TOKEN},
				{"metadata", {{"defined", sourceFilePath}}}
			});

			return true;
		}

		virtual std::string Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics) override { return ""; }
	};

	class LinkPragma : public PragmaHandler
	{
		public:
		LinkPragma() : PragmaHandler(LINK_PRAGMA_TOKEN, {{}, {true}, {true}}, 1) { }

		public:
		virtual bool CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation) override
		{
			std::string objectInput = tokens.size() == 3 ? tokens[1] : sourceFilePath; // TODO: search graph from sourceFilePath to object files
			std::string binaryOutput = tokens.size() == 3 ? tokens[2] : tokens[1];
			
			// Get meta & save object file as node & create connection between source and object file
			auto& meta = Meta::GetInstance(preprocessor);
			meta.json["graph"]["nodes"][sourceFileDir + binaryOutput]["metadata"]["defined"] = sourceFilePath;
			meta.json["graph"]["edges"].push_back
			({
				{"source", objectInput},
				{"target", binaryOutput},
				{"relation", LINK_PRAGMA_TOKEN},
				{"metadata", {{"defined", sourceFilePath}}}
			});

			return true;
		}

		virtual std::string Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics) override { return ""; }
	};
}} // namespace QED::Pragmatic