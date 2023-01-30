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


#define SOURCE_PRAGMA_TOKEN "source"

namespace QED::Pragmatic
{

	class BuildPragma : public PragmaHandler
	{
		public:
		BuildPragma();

		public:
		virtual bool CheckTokens
		(
			clang::Preprocessor &preprocessor,
			std::vector<std::string> tokens,
			clang::DiagnosticsEngine& diagnostics,
			clang::SourceLocation sourceLocation
		) override;

		virtual std::string Response
		(
			clang::Preprocessor &preprocessor,
			std::vector<std::string> tokens,
			clang::DiagnosticsEngine& diagnostics
		) override;
	};

	class LinkPragma : public PragmaHandler
	{
		public:
		LinkPragma();

		public:
		virtual bool CheckTokens
		(
			clang::Preprocessor &preprocessor,
			std::vector<std::string> tokens,
			clang::DiagnosticsEngine& diagnostics,
			clang::SourceLocation sourceLocation
		) override;

		virtual std::string Response
		(
			clang::Preprocessor &preprocessor,
			std::vector<std::string> tokens,
			clang::DiagnosticsEngine& diagnostics
		) override;
	};

	void IncludeCallback(std::string source, std::string target);	
} // namespace QED::Pragmatic