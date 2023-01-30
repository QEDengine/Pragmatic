#pragma once

// Standard library
#include <vector>	// vector
#include <string>	// string
// Clang
#include <clang/Lex/Pragma.h>			// PragmaHandler
#include <clang/Lex/Preprocessor.h>		// PragmaHandlerRegistry
#include <clang/Lex/PreprocessorOptions.h>
// Pragmatic
#include "PragmaHandler.hpp"
#include "Utility.hpp"
#include "clang/Basic/SourceLocation.h"
#include "clang/Basic/SourceManager.h"


namespace QED { namespace Pragmatic
{
	class Callbacks : public clang::PPCallbacks
	{
		protected:
		clang::Preprocessor& preprocessor;
		clang::SourceManager& sourceManager;

		public:
		Callbacks(clang::Preprocessor& preprocessor);

		virtual void FileChanged
		(
			clang::SourceLocation Loc,
			clang::PPCallbacks::FileChangeReason Reason,
			clang::SrcMgr::CharacteristicKind FileType,
			clang::FileID PrevFID
		) override;

		virtual void EndOfMainFile() override;

		virtual void InclusionDirective
		(
			clang::SourceLocation HashLoc,
			const clang::Token &IncludeTok,
			clang::StringRef FileName,
			bool IsAngled,
			clang::CharSourceRange FilenameRange,
			clang::Optional<clang::FileEntryRef> File,
			clang::StringRef SearchPath,
			clang::StringRef RelativePath,
			const clang::Module *Imported,
			clang::SrcMgr::CharacteristicKind FileType
		) override;
	};

	class PreamblePragmaHandler : public PragmaHandler
	{
		public: // Constructor
		PreamblePragmaHandler();

		public: // Clang functions
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
}} // namespace QED::Pragmatic
